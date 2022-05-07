package main

import (
	"fmt"
	"github.com/thanhld9x/onvif/discovery"
	"time"
)

func main() {

	// discovery devices
	devices, err := discovery.StartDiscovery(5 * time.Second)
	if err != nil {
		fmt.Println(err.Error())
	}
	//if len(devices) == 0 {
	//	fmt.Printf("No devices descovered\n")
	//
	//	return
	//}
	//
	fmt.Printf("Discovered %d devices\n", len(devices))
	//pretty.Println(devices)

}
