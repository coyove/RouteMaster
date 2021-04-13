package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"strings"
	"time"

	"github.com/tidwall/gjson"
)

func main() {
	// readBus()
	// return

	// // getBusRoute("12a8f7e3")
	// for i := 'A'; i <= 'Z'; i++ {
	// 	walkBus("https://m.8684.cn/shanghai_list" + string(i))
	// }
	// return

	readRaw := func(path string) []byte {
		buf, _ := ioutil.ReadFile(path)
		return buf[bytes.IndexByte(buf, '\'')+1 : bytes.LastIndexByte(buf, '\'')]
	}

	buf := readRaw("station_name.txt")
	for _, s := range bytes.Split(buf, []byte("@")) {
		tmp := bytes.Split(s, []byte("|"))
		if len(tmp) > 2 {
			stations[string(tmp[1])] = string(tmp[2])
			stations2[string(tmp[2])] = string(tmp[1])
		}
	}

	m, _ := getAllTrains(stations["南京"])
	m2, _ := getAllTrains(stations["上海"])
	dedup := map[string][]string{}
	for k, v := range m {
		if _, ok := m2[k]; ok {
			fn := "data/" + v.CodeHuman + ".json"
			buf, _ := ioutil.ReadFile(fn)
			if len(buf) > 0 {
				json.Unmarshal(buf, &v)
				fmt.Print("LOCAL ")
			} else {
				v.FillPath()
				time.Sleep(time.Second + time.Duration(rand.Intn(200))*time.Millisecond)
				buf, _ = json.Marshal(v)
				ioutil.WriteFile(fn, buf, 0777)
			}
			str := smartJoin(v.Path.Trim("南京", "上海").Stations())
			if !strings.HasPrefix(str, "南京") {
				str = smartJoin(v.Path.Reverse().Trim("南京", "上海").Stations())
			}
			// fmt.Println(v.CodeHuman, str)
			dedup[str] = append(dedup[str], v.CodeHuman)
		}
	}

	for k, v := range dedup {
		fmt.Println(k, v)
	}
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
