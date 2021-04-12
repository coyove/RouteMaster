package main

import (
	"math"
	"strings"
	"time"
)

var (
	stations  = map[string]string{}
	stations2 = map[string]string{}
)

func telecode(in string) string {
	if _, ok := stations2[in]; ok {
		return in
	}
	if stations[in] == "" {
		cand := ""
		for k := range stations {
			if strings.Contains(k, in) {
				if cand == "" || len(k) < len(cand) {
					cand = k
				}
			}
		}
		if cand != "" {
			return stations[cand]
		}
		panic(in)
	}
	return stations[in]
}

func parseTime(date, in string) int64 {
	t, err := time.Parse("2006-01-02 15:04", date+" "+in)
	if err != nil {
		panic(err)
	}
	return t.Unix()
}

func smartJoin(v []string) string {
	for i := range v {
		v[i] = strings.Replace(v[i], "南京南", "南京", -1)
		v[i] = strings.Replace(v[i], "上海南", "上海", -1)
		v[i] = strings.Replace(v[i], "上海虹桥", "上海", -1)
		v[i] = strings.Replace(v[i], "苏州新区", "苏州", -1)
		v[i] = strings.Replace(v[i], "苏州园区", "苏州", -1)
		v[i] = strings.Replace(v[i], "无锡新区", "无锡", -1)
		v[i] = strings.Replace(v[i], "惠山", "无锡", -1)
	}
	for i := len(v) - 2; i >= 0; i-- {
		if v[i] == v[i+1] {
			v = append(v[:i], v[i+1:]...)
		}
	}
	return strings.Join(v, ",")
}

func bd09togcj02(bd_lon, bd_lat float64) (float64, float64) {
	var x_pi = 3.14159265358979324 * 3000.0 / 180.0
	var x = bd_lon - 0.0065
	var y = bd_lat - 0.006
	var z = math.Sqrt(x*x+y*y) - 0.00002*math.Sin(y*x_pi)
	var theta = math.Atan2(y, x) - 0.000003*math.Cos(x*x_pi)
	var gg_lng = z * math.Cos(theta)
	var gg_lat = z * math.Sin(theta)
	return gg_lng, gg_lat
}

/**
 * 火星坐标系 (GCJ-02) 与百度坐标系 (BD-09) 的转换
 * 即谷歌、高德 转 百度
 * @param lng
 * @param lat
 * @returns {*[]}
 */
func gcj02tobd09(lng, lat float64) (float64, float64) {
	var x_pi = 3.14159265358979324 * 3000.0 / 180.0
	var z = math.Sqrt(lng*lng+lat*lat) + 0.00002*math.Sin(lat*x_pi)
	var theta = math.Atan2(lat, lng) + 0.000003*math.Cos(lng*x_pi)
	var bd_lng = z*math.Cos(theta) + 0.0065
	var bd_lat = z*math.Sin(theta) + 0.006
	return bd_lng, bd_lat
}

func cleanText(in string) string {
	r := []rune(in)
	for i := len(r) - 1; i >= 0; i-- {
		if r[i] > 0xa000 {
			r = append(r[:i], r[i+1:]...)
		}
	}
	return string(r)
}
