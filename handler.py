import os
import io
import boto3

from google.cloud import documentai_v1 as documentai

def hello(event, context):
    """
    Processes a document from S3 using the Document AI API.

    Args:
        event (dict): Event data from AWS Lambda.
        context (object): Lambda context object.

    Returns:
        dict: Processed document data or error message.
    """
    try:
        # AWS Lambda environment variables
        # project_id = os.environ['PROJECT_ID']
        # location = os.environ['LOCATION']
        # processor_id = os.environ['PROCESSOR_ID']
        # bucket_name = event['Records'][0]['s3']['bucket']['name']
        # object_key = event['Records'][0]['s3']['object']['key']

        project_id = os.environ['37824744800']
        location = os.environ['us']
        processor_id = os.environ['fb487890d854cfe7']
        bucket_name = 'ts-cu-cer-lib-tra-bucket'
        object_key = 'libertad_y_tradicion_parque_industrial.pdf '

        # Download the document from S3
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read()

        # Set up Document AI client
        opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
        name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

        # Create RawDocument
        raw_document = documentai.RawDocument(content=file_content, mime_type="application/pdf")
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)

        # Process the document
        result = client.process_document(request=request)
        document = result.document

        # Extract form fields and entities
        form_fields_data = []
        for page in document.pages:
            for form_field in page.form_fields:
                field_name = form_field.field_name.text_anchor.content
                field_value = form_field.field_value.text_anchor.content
                form_fields_data.append({"field": field_name, "value": field_value})

        entities_data = []
        if document.entities:
            for entity in document.entities:
                entity_info = {
                    "type": entity.type_,
                    "mention_text": entity.mention_text,
                    "confidence": entity.confidence
                }
                if entity.normalized_value:
                    entity_info["normalized_value"] = entity.normalized_value
                entities_data.append(entity_info)

        return {
            'statusCode': 200,
            'body': {
                'form_fields': form_fields_data,
                'entities': entities_data,
                'document_text': document.text
            }
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }