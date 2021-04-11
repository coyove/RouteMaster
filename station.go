package main

var (
	stations  = map[string]string{}
	stations2 = map[string]string{}
)

func telecode(in string) string {
	if _, ok := stations2[in]; ok {
		return in
	}
	if stations[in] == "" {
		panic(in)
	}
	return stations[in]
}
