#!/bin/bash

echo "Downloaing d2rq tools"
wget https://github.com/downloads/d2rq/d2rq/d2rq-0.8.1.tar.gz;
echo"Done"
tar -xvzf d2rq-0.8.1.tar.gz;
cd d2rq-0.8.1;
for x in {hudong_baike,baidu_baike}; do
    echo "Generating ttl and nt files for $x"
    name_ttl=`echo "kg_demo_mapping_$x.ttl"`
    name_nt=`echo "$x.nt"`
    ./generate-mapping -u root -p nlp -o $name_ttl jdbc:mysql:///$x;
    sed -i '9a \@prefix : <http://www.kgdemo.com#> .' $name_ttl;
    ./dump-rdf -o $name_nt $name_ttl; # get NTriples
done
