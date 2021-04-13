package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math"
	"math/rand"
	"net/http"
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
	"github.com/fogleman/gg"
	"github.com/tidwall/gjson"
)

func readBus() {
	files, _ := ioutil.ReadDir("bus")
	bbox := [2][2]float64{{math.MaxFloat64, math.MaxFloat64}, {-math.MaxFloat64, -math.MaxFloat64}}
	const w, h = 4000, 4000
	g := gg.NewContext(w, h)
	g.DrawRectangle(0, 0, w, h)
	g.SetRGB(0.5, 0.5, 0.5)
	g.Fill()

	baseLon, baseLat := 120.9, 30.6
	rangeLon, rangeLat := 1.2, 1.2

NEXT:
	for _, f := range files {
		buf, _ := ioutil.ReadFile("bus/" + f.Name())
		var m BusRoute
		json.Unmarshal(buf, &m)
		for i := len(m.Stops) - 1; i >= 0; i-- {
			s := m.Stops[i]
			if s.Lat < baseLat || s.Lon < baseLon {
				m.Stops = append(m.Stops[:i], m.Stops[i+1:]...)
				continue NEXT
			}
		}

		for i := len(m.Stops) - 1; i >= 0; i-- {
			if i > 0 && math.Abs(m.Stops[i].Lat-m.Stops[i-1].Lat) > 0.05 {
				m.Stops = append(m.Stops[:i], m.Stops[i+1:]...)
				continue NEXT
			}
			if i > 0 && math.Abs(m.Stops[i].Lon-m.Stops[i-1].Lon) > 0.05 {
				m.Stops = append(m.Stops[:i], m.Stops[i+1:]...)
				continue NEXT
			}
		}

		for i, s := range m.Stops {
			bbox[1][0] = math.Max(bbox[1][0], s.Lon)
			bbox[1][1] = math.Max(bbox[1][1], s.Lat)
			bbox[0][0] = math.Min(bbox[0][0], s.Lon)
			bbox[0][1] = math.Min(bbox[0][1], s.Lat)

			g.SetRGB(1, 1, 1)
			g.DrawPoint((s.Lon-baseLon)/rangeLon*w, h-(s.Lat-baseLat)/rangeLat*h, 1)

			if i > 0 {
				g.DrawLine((s.Lon-baseLon)/rangeLon*w, h-(s.Lat-baseLat)/rangeLat*h,
					(m.Stops[i-1].Lon-baseLon)/rangeLon*w, h-(m.Stops[i-1].Lat-baseLat)/rangeLat*h)

				if m.Stops[i-1].Lat-s.Lat > 0.2 {
					fmt.Println(m.Name)
				}
			}
			g.Stroke()
		}
	}

	g.SavePNG("1.png")
}

func httpGet(u string) (*http.Response, error) {
	req, _ := http.NewRequest("GET", u, nil)
	req.Header.Add("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0")
	return http.DefaultClient.Do(req)
}

func walkBus(u string) bool {
	resp, _ := httpGet(u)
	doc, _ := goquery.NewDocumentFromResponse(resp)
	defer resp.Body.Close()
	doc.Find("a").Each(func(i int, sel *goquery.Selection) {
		link, _ := sel.Attr("href")
		if strings.HasPrefix(link, "/shanghai_x_") {
			fmt.Println(sel.Text(), link)
			getBusRoute(sel.Text(), link[12:])
			time.Sleep(time.Second*2 + time.Duration(rand.Intn(2))*time.Second)
		}
	})
	return true
}

func getBusRoute(name, code string) {
	resp, _ := http.Get("https://api.8684.cn/bus_station_map_station.php?code=" + code + "&ecity=shanghai&kind=1")
	defer resp.Body.Close()
	buf, _ := ioutil.ReadAll(resp.Body)
	stops := []BusStop{}
	for _, s := range gjson.GetBytes(buf, "data").Array() {
		long, lat := s.Get("lng").Float()/1e5, s.Get("lat").Float()/1e5
		stops = append(stops, BusStop{s.Get("t_name").String(), long, lat})
	}
	buf, _ = json.Marshal(BusRoute{
		name,
		code,
		stops,
	})
	ioutil.WriteFile("bus/"+code, buf, 0777)
}

type BusRoute struct {
	Name  string
	Code  string
	Stops []BusStop
}

type BusStop struct {
	Name     string
	Lon, Lat float64
}
