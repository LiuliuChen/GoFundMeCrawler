# GoFundMeCrawler

## Description
This is a crawler, information extractor and sentimental analyzer for GoFundMe website.

## Example Code
1. Collecting urls from website\
```
    url = 'https://www.gofundme.com/start/charity-fundraising'  # homepage
    monitor = Monitor(url)
    monitor.run()
```
2. Extracting information from individual campaign page
```
    monitor.extract()
```
3. Text sentimental analysis
```angular2html
    python run sentimential_analysis.py
```

## Output Data Format
1. Extracted_data
```json
{
    "url":"",
    "collected_date":"",
    "created_date":"",
    "campaign_name":"",
    "location":{
        "city":"",
        "country":"",
        "postal_code":"",
        "state_prefix":""
    },
    "fundraising_team":[
        {
            "name":"",
            "role":"",
            "locale":""
        }
    ],
    "beneficiary":"",
    "description":"",
    "donation":{
        "raised_money":"",
        "goal":""
    },
    "counting":{
        "counts":{
            "total_photos":1,
            "total_co_photos":1,
            "total_community_photos":0,
            "total_comments":5,
            "total_updates":0,
            "total_donations":229,
            "total_unique_donors":227,
            "amount_raised_unattributed":23508.0,
            "number_of_donations_unattributed":229,
            "campaign_hearts":295,
            "social_share_total":133
        },
        "updated_time":"2021-11-23T03:00:38.223927-06:00"
    },
    "comment":[ // comment list
        {
            "comment_id":117356275,
            "name":"Bethlehem Baptist Church",
            "created_time":"2021-11-22T16:32:18",
            "content":"So sorry for your loss. We are upholding your family in prayer.",
            "donation_amount":1000.0,
            "is_anonymous":false
        }
    ],
  "donation_list":[ // donation list
        {
            "donation_id":829567197,
            "amount":250,
            "is_offline":false,
            "is_anonymous":false,
            "created_at":"2021-11-22T18:46:21-06:00",
            "name":"Monique Linder",
            "profile_url":"",
            "verified":true,
            "currencycode":"USD",
            "fund_id":61361573,
            "checkout_id":"72094563"
        }
    ]
}
```
2. Sentimental analysis

|      | Description |
| ----------- | ----------- |
| name      | campaign name       |
| description   | split text of description   |
| pred      | no. of label       |
| label      | predicted emotion class       |
| score      | score of label       |
| anger      | score for each emotion       |
|...       |
## Credits
[emotion-english-distilroberta-base](https://huggingface.co/j-hartmann/emotion-english-distilroberta-base) for text sentimental analysis

[distilbert-base-uncased-go-emotions-student](https://huggingface.co/joeddav/distilbert-base-uncased-go-emotions-student) for text sentimental analysis(GoEmotion)
## License