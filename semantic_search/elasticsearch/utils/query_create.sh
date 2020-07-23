#!/bin/bash
curl -XPUT 'localhost:9200/demo?pretty' -H 'Content-Type: application/json' -d'
{
    "mappings": {
        "baidu_baike": {        
            "properties": {
                "subj": {"type": "keyword"},
                "height": {"type": "integer"},
                "weight": {"type": "integer"},
                "po":{
                    "type": "nested",
                    "properties":{
                        "pred":{"type":"keyword"},
                        "obj":{"type":"keyword"}
                    }
                }            
            }
        }
    }
}
'
