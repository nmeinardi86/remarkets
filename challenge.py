from sys import argv
import sys
import time
import pyRofex
import argparse


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

parser = MyParser()
parser.add_argument('--T', required=True, help='Ticker')
parser.add_argument('--U', required=True, help='Usuario')
parser.add_argument('--P', required=True, help='Pass')
parser.add_argument('--A', required=True, help='Account')

args = parser.parse_args()

#print(args)
#importo los argumentos
#ticker, user, password = argv

ticker = args.T
user = args.U
password = args.P
account = args.A

try:

    print ("Iniciando Sesion en Remarkets")

    pyRofex.initialize(user=user,
                    password=password,
                    account=account,
                    environment=pyRofex.Environment.REMARKET)


    #consulto el ultimo precio del ticker
    print ("Consultando Simbolo", ticker )
    UPO =pyRofex.get_market_data(ticker=ticker,
                            entries=[ pyRofex.MarketDataEntry.LAST])

    if UPO["status"] == "ERROR":
        print("Ticker invalido")
        print ("Cerrando sesión en Remarkets")
        pyRofex.close_websocket_connection()
    else:


        if UPO["marketData"]["LA"] == None:
            print("No hay ultimo precio operado")
        else:
            print ("Ultimo Precio Operado", UPO["marketData"]["LA"]['price'])

        print("Consultando BID")

        #consulto la ultima oferta
        BID =pyRofex.get_market_data(ticker=ticker,
                                entries=[ pyRofex.MarketDataEntry.BIDS])

        OF = BID["marketData"]["BI"]


        if OF == [] :
            print("No hay BIDs activos")

            #genero una orden por 81.5 centavos
            order = pyRofex.send_order(ticker=ticker,
                                side=pyRofex.Side.BUY,
                                size=10,
                                price=81.5,
                                order_type=pyRofex.OrderType.LIMIT)
            
            # Imprimo la respuesta de la orden
            print("Resultado de la orden: {0}".format(order["status"]))

            # Reviso el estado de la orden
            order_status = pyRofex.get_order_status(order["order"]["clientId"])

            # Imprimo el estado de la orden
            print("Estado de la orden: {0}".format(order_status["status"]))


            # si el estado de la orden es PENDING_NEW entonces sigo verificanto el estado
            # hasta que el mercado acepte o rechace la orden o se alcance el tiempo maximo

            timeout = 5 # Time out 5 segundos

            while order_status["order"]["status"] == "PENDING_NEW" and timeout > 0:
                time.sleep(1)
                order_status = pyRofex.get_order_status(order["order"]["clientId"])

                # Imprimo el estado de la orden
                print("Reverificando el estado de la orden: {0}".format(order_status["status"]))

                timeout = timeout - 1


            # si el estado es NEW confirmo que la orden fue creada exitosamente
            if order_status["order"]["status"] == "NEW":
                print("orden creada exitosamente")
                
        else:
            #guardo el precio de la ultima BID
            lbid = OF[0]['price']

            #imprimo la respuesta del mercado
            print("Ultimo BID: {0}".format(lbid))


            newBID = round(lbid-0.01,2)

            #genero una orden por  un centavo menos que la ultima orden
            print("Generando orden por ", newBID)

            order = pyRofex.send_order(ticker=ticker,
                                side=pyRofex.Side.BUY,
                                size=10,
                                price=newBID,
                                order_type=pyRofex.OrderType.LIMIT)
            
            # Imprimo la respuesta de la orden
            print("Resultado de la orden: {0}".format(order["status"]))

            # Reviso el estado de la orden
            order_status = pyRofex.get_order_status(order["order"]["clientId"])

            # Imprimo el estado de la orden
            print("Estado de la orden: {0}".format(order_status["order"]["status"]))


            # si el estado de la orden es PENDING_NEW entonces sigo verificanto el estado
            # hasta que el mercado acepte o rechace la orden o se alcance el tiempo maximo

            timeout = 5 # Time out 5 segundos

            while order_status["order"]["status"] == "PENDING_NEW" and timeout > 0:
                time.sleep(1)
                order_status = pyRofex.get_order_status(order["order"]["clientId"])

                # Imprimo el estado de la orden
                print("Reverificando el estado de la orden: {0}".format(order_status["order"]["status"]))
                print(order_status)
                timeout = timeout - 1


            # si el estado es NEW confirmo que la orden fue creada exitosamente
            if order_status["order"]["status"] == "NEW":
                print("Orden creada exitosamente")
                
                

        #en caso que haya habido un rechazo imprimo el mensaje de rechazo
        if order_status["order"]["status"] == "REJECTED":
            print(order_status["order"]["text"])




        #cerrado cesion 
        print ("Cerrando sesión en Remarkets")



except:
    print ("Se produjo un error durante el inicio de sesion")
