from flask import Flask

# -*- coding: utf-8 -*-
import logging
import commands
_logger = logging.getLogger(__name__)


#from openerp import http
#from openerp.http import request


# drivers modules must add to drivers an object with a get_status() method
# so that 'status' can return the status of all active drivers
drivers = {}

class Proxy():

    def __init__(self):
        self.app = Flask(__name__)

    def get_status(self):
        statuses = {}
        for driver in drivers:
            statuses[driver] = drivers[driver].get_status()
        return statuses

    @app.route('/hw_proxy/hello')
    def hello(self):
        return "ping"

    @app.route('/hw_proxy/handshake')
    def handshake(self):
        return True

    @app.route('/hw_proxy/status')
    def status_http(self):
        resp = """
<!DOCTYPE HTML>
<html>
    <head>
        <title>Odoo's PosBox</title>
        <style>
        body {
            width: 480px;
            margin: 60px auto;
            font-family: sans-serif;
            text-align: justify;
            color: #6B6B6B;
        }
        .device {
            border-bottom: solid 1px rgb(216,216,216);
            padding: 9px;
        }
        .device:nth-child(2n) {
            background:rgb(240,240,240);
        }
        </style>
    </head>
    <body>
        <h1>Hardware Status</h1>
        <p>The list of enabled drivers and their status</p>
"""
        statuses = self.get_status()
        for driver in statuses:

            status = statuses[driver]

            if status['status'] == 'connecting':
                color = 'black'
            elif status['status'] == 'connected':
                color = 'green'
            else:
                color = 'red'

            resp += "<h3 style='color:"+color+";'>"+driver+' : '+status['status']+"</h3>\n"
            resp += "<ul>\n"
            for msg in status['messages']:
                resp += '<li>'+msg+'</li>\n'
            resp += "</ul>\n"
        resp += """
            <h2>Connected Devices</h2>
            <p>The list of connected USB devices as seen by the posbox</p>
        """
        devices = commands.getoutput("lsusb").split('\n')
        resp += "<div class='devices'>\n"
        for device in devices:
            device_name = device[device.find('ID')+2:]
            resp+= "<div class='device' data-device='"+device+"'>"+device_name+"</div>\n"
        resp += "</div>\n"
        resp += """
            <h2>Add New Printer</h2>
            <p>
            Copy and paste your printer's device description in the form below. You can find
            your printer's description in the device list above. If you find that your printer works
            well, please send your printer's description to <a href='mailto:support@odoo.com'>
            support@openerp.com</a> so that we can add it to the default list of supported devices.
            </p>
            <form action='/hw_proxy/escpos/add_supported_device' method='GET'>
                <input type='text' style='width:400px' name='device_string' placeholder='123a:b456 Sample Device description' />
                <input type='submit' value='submit' />
            </form>
            <h2>Reset To Defaults</h2>
            <p>If the added devices cause problems, you can <a href='/hw_proxy/escpos/reset_supported_devices'>Reset the
            device list to factory default.</a> This operation cannot be undone.</p>
        """
        resp += "</body>\n</html>\n\n"

        return request.make_response(resp,{
            'Cache-Control': 'no-cache',
            'Content-Type': 'text/html; charset=utf-8',
            'Access-Control-Allow-Origin':  '*',
            'Access-Control-Allow-Methods': 'GET',
            })

    @app.route('/hw_proxy/status_json')
    def status_json(self):
        return self.get_status()

    @app.route('/hw_proxy/scan_item_success')
    def scan_item_success(self, ean):
        """
        A product has been scanned with success
        """
        print 'scan_item_success: ' + str(ean)

    @app.route('/hw_proxy/scan_item_error_unrecognized')
    def scan_item_error_unrecognized(self, ean):
        """
        A product has been scanned without success
        """
        print 'scan_item_error_unrecognized: ' + str(ean)

    @app.route('/hw_proxy/help_needed')
    def help_needed(self):
        """
        The user wants an help (ex: light is on)
        """
        print "help_needed"

    @app.route('/hw_proxy/help_canceled')
    def help_canceled(self):
        """
        The user stops the help request
        """
        print "help_canceled"

    @app.route('/hw_proxy/payment_request')
    def payment_request(self, price):
        """
        The PoS will activate the method payment
        """
        print "payment_request: price:"+str(price)
        return 'ok'

    @app.route('/hw_proxy/payment_status')
    def payment_status(self):
        print "payment_status"
        return { 'status':'waiting' }

    @app.route('/hw_proxy/payment_cancel')
    def payment_cancel(self):
        print "payment_cancel"

    @app.route('/hw_proxy/transaction_start')
    def transaction_start(self):
        print 'transaction_start'

    @app.route('/hw_proxy/transaction_end')
    def transaction_end(self):
        print 'transaction_end'

    @app.route('/hw_proxy/cashier_mode_activated')
    def cashier_mode_activated(self):
        print 'cashier_mode_activated'

    @app.route('/hw_proxy/cashier_mode_deactivated')
    def cashier_mode_deactivated(self):
        print 'cashier_mode_deactivated'

    @app.route('/hw_proxy/open_cashbox')
    def open_cashbox(self):
        print 'open_cashbox'

    @app.route('/hw_proxy/print_receipt')
    def print_receipt(self, receipt):
        print 'print_receipt' + str(receipt)

    @app.route('/hw_proxy/is_scanner_connected')
    def is_scanner_connected(self, receipt):
        print 'is_scanner_connected?'
        return False

    @app.route('/hw_proxy/scanner')
    def scanner(self, receipt):
        print 'scanner'
        time.sleep(10)
        return ''

    @app.route('/hw_proxy/log')
    def log(self, arguments):
        _logger.info(' '.join(str(v) for v in arguments))

    @app.route('/hw_proxy/print_pdf_invoice')
    def print_pdf_invoice(self, pdfinvoice):
        print 'print_pdf_invoice' + str(pdfinvoice)
