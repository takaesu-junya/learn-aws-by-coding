import os
import argparse, sys, logging
from transformers import pipeline
import boto3

# suppress warning message from pipeline
logging.disable(sys.maxsize)

def main(context, question, item_id, save_flag):

    nlp = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')
    answer = nlp({
        "question": question,
        "context": context
    })

    # store answer in DynamoDB
    if save_flag:
        # パラメータ名のプレフィックスを構築
        student_id = os.environ.get("STUDENT_ID")
        if not student_id:
            raise ValueError("STUDENT_ID environment variable must be set.")
        full_path_table_name = f"/qabot/{student_id}/TABLE_NAME"
        # get the table name
        ssm_client = boto3.client("ssm")
        table_name = ssm_client.get_parameter(Name=full_path_table_name)["Parameter"]["Value"]

        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(table_name)
        resp = table.put_item(
            Item={
                "item_id": item_id,
                "context": context,
                "question": question,
                "score": str(answer["score"]),
                "answer": answer["answer"],
            }
        )

    print(answer)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("context", type=str)
    parser.add_argument("question", type=str)
    parser.add_argument("item_id", type=str)
    parser.add_argument("--no_save", action="store_true")
    args = parser.parse_args()
    main(args.context, args.question, args.item_id, not(args.no_save))
