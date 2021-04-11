package main

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"

	"github.com/tidwall/gjson"
)

func main() {
	buf := readRaw("station_name.txt")
	for _, s := range bytes.Split(buf, []byte("@")) {
		tmp := bytes.Split(s, []byte("|"))
		if len(tmp) > 2 {
			stations[string(tmp[1])] = string(tmp[2])
			stations2[string(tmp[2])] = string(tmp[1])
		}
	}

	m := getAllTrains(stations["南京"])
	getTrainInfo(m[0])
}

func readRaw(path string) []byte {
	buf, _ := ioutil.ReadFile(path)
	return buf[bytes.IndexByte(buf, '\'')+1 : bytes.LastIndexByte(buf, '\'')]
}

func getAllTrains(code string) []Run {
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
			}
		}
		return m
	}
	m := getter(1)
	for i := 2; i < 4; i++ {
		for k, v := range getter(i) {
			m[k] = v
		}
	}
	f := make([]Run, 0, len(m))
	for _, v := range m {
		f = append(f, v)
	}
	return f
}

func getTrainInfo(r Run) {
	u := fmt.Sprintf("https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=%s&from_station_telecode=%s&to_station_telecode=%s&depart_date="+
		time.Now().AddDate(0, 0, 1).Format("2006-01-02"), r.Code, telecode(r.From), telecode(r.To))
	resp, _ := http.Get(u)
	defer resp.Body.Close()
	buf, _ := ioutil.ReadAll(resp.Body)
	for _, p := range gjson.GetBytes(buf, "data.data").Array() {
		fmt.Println(p)
	}
}

type Run struct {
	Code      string
	CodeHuman string
	From, To  string
}
