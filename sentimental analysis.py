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

    campaign_name, description =[], []
    with open('data/CampaignData_new_formatted.txt', 'r', encoding='utf-8') as f:
        data = json.loads(f.read())

    for i in data:
        campaign_name.append(i['campaign_name'])
        description.append(i['description'])


    # Tokenize texts and create prediction data set
    tokenized_texts = tokenizer(description,truncation=True,padding=True)
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
    anger = []
    disgust = []
    fear = []
    joy = []
    neutral = []
    sadness = []
    surprise = []

    # extract scores (as many entries as exist in pred_texts)
    for i in range(len(description)):
      anger.append(temp[i][0])
      disgust.append(temp[i][1])
      fear.append(temp[i][2])
      joy.append(temp[i][3])
      neutral.append(temp[i][4])
      sadness.append(temp[i][5])
      surprise.append(temp[i][6])


    # Create DataFrame with texts, predictions, labels, and scores
    df = pd.DataFrame(list(zip(campaign_name, description,preds,labels,scores,  anger, disgust, fear, joy, neutral, sadness, surprise)), columns=['name','description','pred','label','score', 'anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise'])
    df.to_csv('data/sentimental_analysis_full_text.csv', index=False)