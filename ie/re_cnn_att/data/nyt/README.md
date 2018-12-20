# Toolkit for processing NYT10 data

## About the Dataset

NYT10 is a distantly supervised dataset originally released by the paper "Sebastian Riedel, Limin Yao, and Andrew McCallum. Modeling relations and their mentions without labeled text.". Here is the download [link](http://iesl.cs.umass.edu/riedel/ecml/) for the original data.

## Format of the Data

The original data is in the format of protobuf, which is not reading-friendly and requires complex processing in training. We then provide a tool to convert this dataset to json data with the format that meets requirements of [OpenNRE](https://github.com/thunlp/OpenNRE).

## How to Use

1. Generate `Document_pb2.py` (which we have provided in the toolkit but does't exist in the original data)

```
protoc --proto_path=. --python_out=. Document.proto
```

2. Run `protobuf2json.py`

```
python protobuf2json.py
```

Then you will get `train.json`, `test.json` and their reading-friendly version `train-reading-friendly.json` and `test-reading-friendly.json`. Besides, we've provided `nyt_word_vec.json` and `rel2id.json`, which you will need for OpenNRE.

