package main

import (
	"archive/zip"
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"os"
	"strings"
	"time"
	"unicode"
	"unicode/utf16"

	"github.com/PuerkitoBio/goquery"
	"go.etcd.io/bbolt"
)

func main() {
	rand.Seed(time.Now().Unix())
	db, _ := bbolt.Open("icon.db", 0777, nil)

	if true {
		zipFile, _ := os.Create("icon.zip")
		defer zipFile.Close()

		zipWriter := zip.NewWriter(zipFile)
		defer zipWriter.Close()

		db.View(func(tx *bbolt.Tx) error {
			data := tx.Bucket([]byte("data"))
			meta := tx.Bucket([]byte("meta"))

			c := data.Cursor()
			i := 0
			cats := map[string][]string{}

			for k, v := c.First(); k != nil; k, v = c.Next() {
				metaV := meta.Get(k)
				if len(metaV) == 0 {
					panic(string(k))
				}

				m := map[string]string{}
				json.Unmarshal(metaV, &m)

				p := SplitByPunct(m["cat"])
				p = append(p, SplitByPunct(m["desc"])...)
				for _, p := range p {
					p = strings.ToLower(p)
					cats[p] = append(cats[p], string(k))
				}

				// fmt.Println(string(k), string(v))
				v = bytes.TrimPrefix(v, []byte("\xef\xbb\xbf"))
				v = bytes.Replace(v, []byte("iso-8859-1"), []byte("utf-8"), 1)
				v = bytes.Replace(v, []byte("us-ascii"), []byte("utf-8"), 1)
				v = []byte(strings.ToValidUTF8(string(v), ""))

				if false {
					idx := bytes.Index(v, []byte("<?"))
					idx2 := bytes.Index(v, []byte("?>"))
					if idx > -1 && idx2 > idx {
						v = v[idx2+2:]
					}
				}

				w, _ := zipWriter.Create(string(k))
				w.Write(v)

				if i++; i%100 == 0 {
					fmt.Println(time.Now().Format("15:04:05"), "data cp", i)
				}
			}

			buf, _ := json.Marshal(cats)
			// ioutil.WriteFile("meta.json", buf, 0777)
			w, _ := zipWriter.Create("meta.json")
			w.Write(buf)
			return nil
		})
		return
	}

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
						if bytes.HasPrefix(data, []byte{254, 255}) {
							x := make([]uint16, len(data)/2)
							for i := 2; i < len(data); i += 2 {
								x = append(x, uint16(data[i])*16+uint16(data[i+1]))
							}
							tmp := utf16.Decode(x)
							data = []byte(string(tmp))
						}
						if !bytes.Contains(data, []byte("<svg")) {
							fmt.Println("\t\terror", data[:10], string(data))
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

func SplitByPunct(in string) (parts []string) {
	i := 0
	runes := []rune(in)
	for ii, r := range runes {
		if unicode.IsPunct(r) || unicode.IsSpace(r) {
			tmp := runes[i:ii]
			if len(tmp) > 0 {
				parts = append(parts, string(tmp))
			}
			i = ii + 1
		} else if ii == len(runes)-1 {
			tmp := runes[i : ii+1]
			if len(tmp) > 0 {
				parts = append(parts, string(tmp))
			}
			break
		}
	}
	return parts
}
