# config.py
CONTRACT_ADDRESS = '0x44A8F09d37489ec423404461E899467eD6cBA539'

CONTRACT_ABI = [
   {
       "constant": False,
       "inputs": [
           {
               "internalType": "string",
               "name": "_name", 
               "type": "string"
           },
           {
               "internalType": "string",
               "name": "_origin",
               "type": "string"
           }
       ],
       "name": "createProduct",
       "outputs": [],
       "payable": False,
       "stateMutability": "nonpayable",
       "type": "function"
   },
   {
       "constant": False,
       "inputs": [
           {
               "internalType": "uint256",
               "name": "_id",
               "type": "uint256"
           }
       ],
       "name": "deliverProduct", 
       "outputs": [],
       "payable": False,
       "stateMutability": "nonpayable",
       "type": "function"
   },
   {
       "anonymous": False,
       "inputs": [
           {
               "indexed": False,
               "internalType": "uint256",
               "name": "id",
               "type": "uint256"
           },
           {
               "indexed": False,
               "internalType": "string",
               "name": "name",
               "type": "string"
           },
           {
               "indexed": False,
               "internalType": "string",
               "name": "origin",
               "type": "string"
           },
           {
               "indexed": False,
               "internalType": "address",
               "name": "producer",
               "type": "address"
           }
       ],
       "name": "ProductCreated",
       "type": "event"
   },
   {
       "anonymous": False,
       "inputs": [
           {
               "indexed": False,
               "internalType": "uint256",
               "name": "id",
               "type": "uint256"
           }
       ],
       "name": "ProductDelivered",
       "type": "event"
   },
   {
       "anonymous": False,
       "inputs": [
           {
               "indexed": False,
               "internalType": "uint256", 
               "name": "id",
               "type": "uint256"
           }
       ],
       "name": "ProductInTransit",
       "type": "event"
   },
   {
       "constant": False,
       "inputs": [
           {
               "internalType": "uint256",
               "name": "_id",
               "type": "uint256" 
           }
       ],
       "name": "shipProduct",
       "outputs": [],
       "payable": False,
       "stateMutability": "nonpayable",
       "type": "function"
   },
   {
       "constant": True,
       "inputs": [],
       "name": "productCount",
       "outputs": [
           {
               "internalType": "uint256",
               "name": "",
               "type": "uint256"
           }
       ],
       "payable": False,
       "stateMutability": "view",
       "type": "function"
   },
   {
       "constant": True,
       "inputs": [
           {
               "internalType": "uint256",
               "name": "",
               "type": "uint256"
           }
       ],
       "name": "products",
       "outputs": [
           {
               "internalType": "uint256",
               "name": "id",
               "type": "uint256"
           },
           {
               "internalType": "string", 
               "name": "name",
               "type": "string"
           },
           {
               "internalType": "string",
               "name": "origin", 
               "type": "string"
           },
           {
               "internalType": "uint256",
               "name": "timestamp",
               "type": "uint256"
           },
           {
               "internalType": "address",
               "name": "producer",
               "type": "address" 
           },
           {
               "internalType": "enum SupplyChain.Status",
               "name": "status",
               "type": "uint8"
           }
       ],
       "payable": False,
       "stateMutability": "view",
       "type": "function"
   }
]