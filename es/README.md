### Data Collection Script

#### Python Prerequisites
`pip install elasticsearch elasticsearch_dsl`

#### Usage
1. `export ES_USERNAME=XXXX`
2. `export ES_PASSWORD=XXXX`
3. `./iris-es-to-ml.py -s <start time> -e <end time>`
4. Data will be written to `./transfer-events.csv`

Example:

    ES_USERNAME=XXXX ES_PASSWORD=XXXX ./iris-es-to-ml.py -s 2020-05-05T00:00:00 -e 2020-05-05T23:59:59
