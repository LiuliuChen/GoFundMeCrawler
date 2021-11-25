import json
import torch
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer


# Create class for data preparation
class SimpleDataset:
    def __init__(self, tokenized_texts):
        self.tokenized_texts = tokenized_texts

    def __len__(self):
        return len(self.tokenized_texts["input_ids"])

    def __getitem__(self, idx):
        return {k: v[idx] for k, v in self.tokenized_texts.items()}

if __name__ == '__main__':

    # Load tokenizer and model, create trainer
    model_name = "j-hartmann/emotion-english-distilroberta-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    trainer = Trainer(model=model)


    # import data
    campaign_name, description, url = [], [], []
    with open('data/CampaignData_new_formatted.txt', 'r', encoding='utf-8') as f:
        data = json.loads(f.read())

    # work in progress
    # container
    anger = []
    disgust = []
    fear = []
    joy = []
    neutral = []
    sadness = []
    surprise = []

    sum_label = []
    sum_pred = []
    sum_score = []
    sum_name = []
    sum_desc = []

    for i in data:
        campaign_name.append(i['campaign_name'])
        url.append(i['url'])
        description.append(i['description'])

        # split description into sentences
        pred_texts = []
        texts = i['description'].strip('\n').strip()
        texts = texts.split('\n')[0]
        pred_texts.append(texts)
        # print('pred_text', pred_texts)

        # Tokenize texts and create prediction data set
        tokenized_texts = tokenizer(pred_texts,truncation=True,padding=True)
        pred_dataset = SimpleDataset(tokenized_texts)

        # Run predictions
        predictions = trainer.predict(pred_dataset)


        # Transform predictions to labels
        preds = predictions.predictions.argmax(-1)
        labels = pd.Series(preds).map(model.config.id2label)
        scores = (np.exp(predictions[0])/np.exp(predictions[0]).sum(-1,keepdims=True)).max(1)

        # scores raw
        temp = (np.exp(predictions[0])/np.exp(predictions[0]).sum(-1,keepdims=True))


        # work in progress
        # container
        anger_i = []
        disgust_i = []
        fear_i = []
        joy_i = []
        neutral_i = []
        sadness_i = []
        surprise_i = []

        # # extract scores (as many entries as exist in pred_texts)
        # for j in range(len(pred_texts)):
        #   anger_i.append(temp[j][0])
        #   disgust_i.append(temp[j][1])
        #   fear_i.append(temp[j][2])
        #   joy_i.append(temp[j][3])
        #   neutral_i.append(temp[j][4])
        #   sadness_i.append(temp[j][5])
        #   surprise_i.append(temp[j][6])
        #
        # anger.append(sum(anger_i)/len(anger_i))
        # disgust.append(sum(disgust_i)/len(disgust_i))
        # fear.append(sum(fear_i)/len(fear_i))
        # joy.append(sum(joy_i)/len(joy_i))
        # neutral.append(sum(neutral_i)/len(neutral_i))
        # sadness.append(sum(sadness_i)/len(sadness_i))
        # surprise.append(sum(surprise_i)/len(surprise_i))
        #
        # # print('type of score_label: ', type(scores), scores)
        # sum_label.append(labels.mode()[0])  # find the most frequent
        # sum_pred.append(np.bincount(preds).argmax())  # find the most frequent
        # sum_score.append(scores.mean()) # average the score

        for j in range(len(pred_texts)):
            anger.append(temp[j][0])
            disgust.append(temp[j][1])
            fear.append(temp[j][2])
            joy.append(temp[j][3])
            neutral.append(temp[j][4])
            sadness.append(temp[j][5])
            surprise.append(temp[j][6])
            sum_name.append(i['campaign_name'])


        sum_pred.extend(preds)
        sum_score.extend(scores)
        sum_label.extend(labels)
        sum_desc.extend(pred_texts)



    # Create DataFrame with texts, predictions, labels, and scores
    df = pd.DataFrame(list(zip(sum_name, url, sum_desc, sum_pred, sum_label, sum_score,  anger, disgust, fear, joy, neutral, sadness, surprise)), columns=['name', 'url', 'description','pred','label','score', 'anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise'])
    df.to_csv('data/sentimental_analysis_1st_graph.csv', index=False)