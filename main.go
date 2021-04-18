package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
	"github.com/tidwall/gjson"
	"go.etcd.io/bbolt"
)

func updateMeta(f func(map[string]map[string]string)) {
	m := map[string]map[string]string{}
	buf, _ := ioutil.ReadFile("block/meta.json")
	json.Unmarshal(buf, &m)
	f(m)
	buf, _ = json.Marshal(m)
	ioutil.WriteFile("block/meta.json", buf, 0777)
}

func main() {
	resp, err := http.Get("https://en.wikipedia.org/wiki/Template:Bsicon")
	if err != nil {
	}
	defer resp.Body.Close()
	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
	}

	links := [][2]string{}
	doc.Find("a").Each(func(i int, sel *goquery.Selection) {
		a, _ := sel.Attr("href")
		if strings.Contains(a, "/BSicon/Catalogue/") {
			links = append(links, [2]string{a, clean(sel.Text())})
		}
	})

	rand.Seed(time.Now().Unix())
	db, _ := bbolt.Open("icon.db", 0777, nil)

	for _, l := range links {
		func(p [2]string) {
			a := p[0]
			fmt.Println("get", a, p[1])
			resp, _ := http.Get(a)
			defer resp.Body.Close()
			doc, _ := goquery.NewDocumentFromReader(resp.Body)
			fmt.Println(os.MkdirAll("block/"+p[1], 0777))
			doc.Find("a").Each(func(i int, sel *goquery.Selection) {
				if a, _ := sel.Attr("href"); strings.HasSuffix(a, ".svg") {
					if sel.Find("img").Length() == 0 && !strings.Contains(a, "File:") {
						return
					}

					name := a[strings.Index(a, "File:")+5:]
					existed := false
					db.View(func(tx *bbolt.Tx) error {
						bk := tx.Bucket([]byte("data"))
						if bk == nil {
							return nil
						}
						data := bk.Get([]byte(name))
						existed = len(data) > 0
						return nil
					})

					if existed {
						return
					}

					a = "https://commons.wikimedia.org" + a
					resp, err := http.Get(a)
					if err != nil {
						fmt.Println(a, err)
						return
					}

					doc, err := goquery.NewDocumentFromReader(resp.Body)
					if err != nil {
						fmt.Println(a, err)
						return
					}
					link, _ := doc.Find(".fullMedia a").First().Attr("href")
					if link == "" {
						src, _ := sel.Find("img").Attr("src")
						src = strings.Replace(src, "/thumb/", "/", -1)
						fmt.Println("==========", src)
					}

					desc := strings.TrimSpace(sel.Parent().Parent().Find("td").Last().Text())
					desc2 := strings.TrimSpace(strings.Replace(doc.Find("div.mw-content-ltr.en.description").First().Text(), "English:", "", 1))
					resp.Body.Close()
					if desc == "" {
						desc = desc2
					}

					fmt.Println(p[1], name, link, desc)
					db.Update(func(tx *bbolt.Tx) error {
						bk, _ := tx.CreateBucketIfNotExists([]byte("meta"))
						m := map[string]string{
							"desc": desc,
							"link": link,
							"cat":  p[1],
						}
						buf, _ := json.Marshal(m)
						bk.Put([]byte(name), buf)

						bk, _ = tx.CreateBucketIfNotExists([]byte("data"))
						data := bk.Get([]byte(name))
						if len(data) > 0 {
							return nil
						}

						resp, err := http.Get(link)
						if err != nil {
							return err
						}
						defer resp.Body.Close()

						data, _ = ioutil.ReadAll(resp.Body)
						if !bytes.Contains(data, []byte("<svg")) {
							fmt.Println("\t\terror")
							return nil
						}
						fmt.Println("\t\t", len(data))
						bk.Put([]byte(name), data)
						return nil
					})
					// download(link, "block/"+p[1]+"/"+name)
					time.Sleep(time.Duration(rand.Intn(100))*time.Millisecond + time.Millisecond*900)
				}
			})
		}(l) // (links[rand.Intn(len(links))])
	}
}

func clean(in string) string {
	in = strings.Replace(in, ", ", "~", -1)
	tmp := []rune(in)
	for i, r := range tmp {
		if r >= 'a' && r <= 'z' {
			continue
		}
		if r >= 'A' && r <= 'Z' {
			continue
		}
		if r >= '0' && r <= '9' {
			continue
		}
		if r == '.' || r == '_' || r == '-' || r == '~' {
			continue
		}
		tmp[i] = '_'
	}
	in = string(tmp)
	in = strings.TrimSuffix(in, "_")
	in = strings.TrimPrefix(in, "_")
	for strings.Index(in, "__") >= 0 {
		in = strings.Replace(in, "__", "_", -1)
	}
	return in
}

func likelyID(in string) bool {
	c := 0
	for _, r := range in {
		if r >= 'A' && r <= 'Z' {
			c++
		}
	}
	return c > 1
}

func getAllTrains(code string) (map[string]Run, []Run) {
	getter := func(d int) map[string]Run {
		now := time.Now().UTC().Add(8*time.Hour).AddDate(0, 0, d).Format("2006-01-02")
		u := fmt.Sprintf("https://kyfw.12306.cn/otn/czxx/query?train_start_date=%s&train_station_code=%s", now, code)
		resp, _ := http.Get(u)
		defer resp.Body.Close()
		buf, _ := ioutil.ReadAll(resp.Body)
		m := map[string]Run{}
		for _, a := range gjson.GetBytes(buf, "data.data").Array() {
			m[a.Get("train_no").Str] = Run{
				Code:      a.Get("train_no").String(),
				CodeHuman: a.Get("station_train_code").String(),
				From:      a.Get("start_station_name").String(),
				To:        a.Get("end_station_name").String(),
				Date:      now,
			}
		}
		return m
	}
	m := getter(1)
	// for i := 2; i < 4; i++ {
	// 	for k, v := range getter(i) {
	// 		m[k] = v
	// 	}
	// }
	f := make([]Run, 0, len(m))
	for _, v := range m {
		f = append(f, v)
	}
	return m, f
}

func (r *Run) FillPath() {
	date := r.Date
	u := fmt.Sprintf("https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=%s&from_station_telecode=%s&to_station_telecode=%s&depart_date="+date,
		r.Code, telecode(r.From), telecode(r.To))
	resp, _ := http.Get(u)
	defer resp.Body.Close()
	buf, _ := ioutil.ReadAll(resp.Body)
	x := gjson.GetBytes(buf, "data.data").Array()
	pt := make(Path, 0, len(x))
	for i, p := range x {
		if i == 0 {
			pt = append(pt, Path1{
				StationName:   p.Get("station_name").String(),
				DepartureTime: parseTime(date, p.Get("start_time").String()),
			})
		} else if i == len(x)-1 {
			pt = append(pt, Path1{
				StationName: p.Get("station_name").String(),
				ArrivalTime: parseTime(date, p.Get("arrive_time").String()),
			})
		} else {
			pt = append(pt, Path1{
				StationName:   p.Get("station_name").String(),
				ArrivalTime:   parseTime(date, p.Get("arrive_time").String()),
				DepartureTime: parseTime(date, p.Get("start_time").String()),
			})
		}
	}
	r.Path = pt
}

type Run struct {
	Date      string
	Code      string
	CodeHuman string
	From, To  string
	Path      Path
}
