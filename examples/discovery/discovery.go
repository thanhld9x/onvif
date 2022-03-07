package main

import (
	"fmt"
	"github.com/thanhld9x/onvif/profiles/media2"
	"log"
	"time"

	"github.com/kr/pretty"
	"github.com/thanhld9x/onvif/discovery"
	"github.com/thanhld9x/onvif/soap"
)

func main() {

	// discovery devices
	devices, err := discovery.StartDiscovery(5 * time.Second)
	if err != nil {
		fmt.Println(err.Error())
	}
	if len(devices) == 0 {
		fmt.Printf("No devices descovered\n")

		return
	}

	fmt.Printf("Discovered %d devices\n", len(devices))
	pretty.Println(devices)

	// Create soap client
	client := soap.NewClient(
		soap.WithTimeout(time.Second * 5),
	)
	client.AddHeader(soap.NewWSSSecurityHeader("admin", "123456789aA", time.Now()))

	// Create devicemgmt service instance and specify xaddr (which could be received in the discovery)
	dev := media2.NewMedia2(client, "http://192.168.2.22/onvif/Media")

	log.Println("devicemgmt.GetServices", "http://192.168.2.22/onvif/Media2")
	{
		reply, err := dev.GetProfiles(&media2.GetProfiles{})
		if err != nil {
			if serr, ok := err.(*soap.SOAPFault); ok {
				pretty.Println(serr)
			}
			log.Fatalf("Request failed: %s", err.Error())
		}
		pretty.Println(reply)
	}

}
