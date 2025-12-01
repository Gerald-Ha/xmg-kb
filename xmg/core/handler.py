# ------------------------------------------------------------------------------
# XMG-KB - RGB Keyboard Controller
# Version: 2.0.5
# Author: Gerald Hasani
# Email: contact@gerald-hasani.com
# GitHub: https://github.com/Gerald-Ha
# ------------------------------------------------------------------------------

import usb.core
import usb.util
import sys


class USBDevice:
    """Basisklasse für USB-Geräteverbindung"""
    
    def __init__(self, vendor_id, product_id):
        self._device = self._connect(vendor_id, product_id)
        cfg = self._device.get_active_configuration()
        self.in_ep = self._find_endpoint(cfg[(1, 0)], usb.util.ENDPOINT_IN)
        self.out_ep = self._find_endpoint(cfg[(1, 0)], usb.util.ENDPOINT_OUT)

    def _connect(self, vendor_id, product_id):
        """Verbindet mit dem USB-Gerät"""
        device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        
        if device is None:
            raise ValueError('Tastatur nicht gefunden! Ist sie angeschlossen?')
        
        # Linux: Kernel-Treiber trennen falls aktiv
        if not sys.platform.startswith('win'):
            if device.is_kernel_driver_active(1):
                device.detach_kernel_driver(1)
        
        return device

    def _find_endpoint(self, interface, ep_type):
        """Findet den USB-Endpoint"""
        return usb.util.find_descriptor(
            interface,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == ep_type
        )


class KeyboardController(USBDevice):
    """Controller für die RGB-Tastaturbeleuchtung"""
    
    def __init__(self, vendor_id, product_id):
        super().__init__(vendor_id, product_id)
        self._request_type = 0x21
        self._request = 0x09
        self._value = 0x300
        self._index = 1

    def ctrl_write(self, *data):
        """Sendet Steuerungsdaten an die Tastatur"""
        self._device.ctrl_transfer(
            self._request_type, 
            self._request, 
            self._value, 
            self._index, 
            data
        )

    def bulk_write(self, times=1, payload=None):
        """Sendet Bulk-Daten an die Tastatur"""
        for _ in range(times):
            self._device.write(self.out_ep, payload)

