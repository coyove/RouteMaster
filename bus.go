package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
	"github.com/tidwall/gjson"
)

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
