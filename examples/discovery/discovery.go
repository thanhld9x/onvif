package main

import (
	"fmt"
	"github.com/thanhld9x/onvif/profiles/analytics"
	"github.com/thanhld9x/onvif/profiles/devicemgmt"
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
	mediaDev := devicemgmt.NewDevice(client, devices[0].XAddr)

	log.Println("devicemgmt.NewDevice", devices[0].XAddr)
	{
		reply, err := mediaDev.GetCapabilities(&devicemgmt.GetCapabilities{})
		if err != nil {
			if serr, ok := err.(*soap.SOAPFault); ok {
				pretty.Println(serr)
			}
			log.Fatalf("Request failed: %s", err.Error())
		}
		pretty.Println(reply)
	}

	// Create devicemgmt service instance and specify xaddr (which could be received in the discovery)
	dev := analytics.NewAnalyticsEnginePort(client, "http://192.168.2.22/onvif/Analytics")

	log.Println("devicemgmt.GetServices", "http://192.168.2.22/onvif/Events")
	{
		reply, err := dev.GetAnalyticsModules(&analytics.GetAnalyticsModules{ConfigurationToken: "VideoAnalyticsToken"})
		if err != nil {
			if serr, ok := err.(*soap.SOAPFault); ok {
				pretty.Println(serr)
			}
			log.Fatalf("Request failed: %s", err.Error())
		}
		pretty.Println(reply)
	}

	ruleDev := analytics.NewRuleEnginePort(client, "http://192.168.2.22/onvif/Analytics")

	log.Println("devicemgmt.GetServices", "http://192.168.2.22/onvif/Events")
	{
		reply, err := ruleDev.GetSupportedRules(&analytics.GetSupportedRules{ConfigurationToken: "VideoAnalyticsToken"})
		if err != nil {
			if serr, ok := err.(*soap.SOAPFault); ok {
				pretty.Println(serr)
			}
			log.Fatalf("Request failed: %s", err.Error())
		}
		pretty.Println(reply)
	}

}
