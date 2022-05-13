package main

import (
	"fmt"
	"github.com/kr/pretty"
	"github.com/thanhld9x/onvif/discovery"
	"github.com/thanhld9x/onvif/profiles/devicemgmt"
	"github.com/thanhld9x/onvif/profiles/media"
	"github.com/thanhld9x/onvif/soap"
	"log"
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

	// Create soap client
	client := soap.NewClient(
		soap.WithTimeout(time.Second*5),
		soap.WithBasicAuth("broadflow", "Red57Covers"),
	)

	// Create devicemgmt service instance and specify xaddr (which could be received in the discovery)
	mediaDev := devicemgmt.NewDevice(client, "http://73.245.135.144:8062/onvif/device_service")
	// http://192.168.2.22/onvif/Media
	// http://192.168.2.22/onvif/device_service
	log.Println("devicemgmt.NewDevice")
	{
		systemDateAndTimeResponse, err := mediaDev.GetSystemDateAndTime(&devicemgmt.GetSystemDateAndTime{})
		if err != nil {
			if serr, ok := err.(*soap.SOAPFault); ok {
				pretty.Println(serr)
			}
			log.Fatalf("Request failed: %s", err.Error())
		}
		deviceTime, _ := systemDateAndTimeResponse.SystemDateAndTime.GetUTCTime()
		timeDiff := deviceTime.Sub(time.Now().UTC())
		client.UpdateOption(soap.WithTimeDiff(timeDiff))

		capacites, err := mediaDev.GetCapabilities(&devicemgmt.GetCapabilities{})
		if err != nil {
			if serr, ok := err.(*soap.SOAPFault); ok {
				pretty.Println(serr)
			}
			log.Fatalf("Request failed: %s", err.Error())
		}
		fmt.Println(capacites)

		replyDevice, err := mediaDev.GetServices(&devicemgmt.GetServices{})
		if err != nil {
			if serr, ok := err.(*soap.SOAPFault); ok {
				pretty.Println(serr)
			}
			log.Fatalf("Request failed: %s", err.Error())
		}

		_, err = mediaDev.GetAccessPolicy(&devicemgmt.GetAccessPolicy{})
		if err != nil {
			if serr, ok := err.(*soap.SOAPFault); ok {
				pretty.Println(serr)
			}
			log.Fatalf("Request failed: %s", err.Error())
		}
		fmt.Println(replyDevice)

		mediaDev3 := media.NewMedia(client, "http://73.245.135.144:8062/onvif/services")

		mediares, err := mediaDev3.GetVideoEncoderConfigurations(&media.GetVideoEncoderConfigurations{})
		if err != nil {
			if serr, ok := err.(*soap.SOAPFault); ok {
				pretty.Println(serr)
			}
			log.Fatalf("Request failed: %s", err.Error())
		}
		fmt.Println(mediares)

	}

}
