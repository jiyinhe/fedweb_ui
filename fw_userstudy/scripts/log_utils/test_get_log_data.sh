#curl -u 9767LR2hn1IQ9WTNaEXqhVoYVSnFcfe0MU4KB9SSZLY: http://ilpslogging.staging.dispectu.com/api/v0/query -d '{
#	"size": 1000,
#  "query": {
#    "match_all": {}
#  }
#}'

#curl -u Zn96VSPzNsoxtyBYUeXmOWlVggtgPNUEOJt0QiuNWGI: http://zookst9.science.uva.nl:8005/api/v0/query -d '{
#	"size": 100000,
#  "query": {
#    "term":{
#		"ip_address": "145.18.160.152"
#	}
#  }
#}'

curl -u ROkhhErhpuiNN5Bpk1HyRegzrOuyKRqx95I3LGXqpi4: http://zookst9.science.uva.nl:8005/api/v0/query -d '{
	"size": 1000000,
  "query": {
	
    "term":{
	"user_id": "'$1'"
}  
	}
}'

#	"ip_address": "145.18.160.152"
#	"match_all": {}
#    "term":{
#	"user_id": "mbron"
#  }

