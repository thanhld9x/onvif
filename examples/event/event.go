package main

import (
	"fmt"
	"github.com/thanhld9x/onvif/profiles/event"
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

	eventClient := event.NewEventPortType(client, "http://192.168.2.22/onvif/Events")

	log.Println("devicemgmt.GetEvent", "http://192.168.2.22/onvif/Events")
	{
		point, err := eventClient.CreatePullPointSubscription(&event.CreatePullPointSubscription{})
		if err != nil {
			if serr, ok := err.(*soap.SOAPFault); ok {
				pretty.Println(serr)
			}
			log.Println("Request failed: %s", err.Error(), point)
		}

		listener := event.NewPullPointSubscription(client, string(point.SubscriptionReference.Address))
		tmp, err := listener.PullMessages(&event.PullMessages{MessageLimit: 20})
		if err != nil {
			if serr, ok := err.(*soap.SOAPFault); ok {
				pretty.Println(serr)
			}
			log.Fatalf("Request failed: %s", err.Error())
		}
		log.Fatalf("listener failed: %s", tmp)

	}

}
