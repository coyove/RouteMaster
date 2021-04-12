package main

import (
	"fmt"
	"strings"
	"time"
)

type Path1 struct {
	StationName   string
	ArrivalTime   int64
	DepartureTime int64
}

type Path []Path1

func (p Path1) String() string {
	if p.ArrivalTime == 0 {
		return fmt.Sprintf("(%s %s 始发)", p.StationName, time.Unix(p.DepartureTime, 0).Format("01-02 15:04"))
	}
	if p.DepartureTime == 0 {
		return fmt.Sprintf("(%s %s 终到)", p.StationName, time.Unix(p.ArrivalTime, 0).Format("01-02 15:04"))
	}
	return fmt.Sprintf("(%s %s 到 %s 发)", p.StationName, time.Unix(p.ArrivalTime, 0).Format("15:04"), time.Unix(p.DepartureTime, 0).Format("15:04"))
}

func (p Path) Stations() []string {
	r := make([]string, len(p))
	for i := range r {
		r[i] = p[i].StationName
	}
	return r
}

func (p Path) Reverse() Path {
	p2 := make(Path, len(p))
	for i := len(p) - 1; i >= 0; i-- {
		p2 = append(p2, p[i])
	}
	return p2
}

func (p Path) Trim(a, b string) Path {
	left := ""
	for i := range p {
		if strings.Contains(p[i].StationName, a) {
			p = p[i:]
			left = b
			break
		}
		if strings.Contains(p[i].StationName, b) {
			p = p[i:]
			left = a
			break
		}
	}
	for i := range p {
		if strings.Contains(p[i].StationName, left) {
			p = p[:i+1]
			break
		}
	}
	return p
}
