import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

# Initialize DynamoDB (if accessible)
try:
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ShoppingCart')
    DYNAMODB_AVAILABLE = True
except Exception:
    DYNAMODB_AVAILABLE = False

# Helper function to convert Decimal to JSON-serializable types
def decimal_to_json(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj

def lambda_handler(event, context):
    try:
        http_method = event['httpMethod']
        # Use hardcoded userId for testing if authorizer is unavailable
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('cognito:username', 'testuser')
        
        if http_method == 'POST':
            # Handle adding an item to the cart
            body = json.loads(event['body'])
            item_id = body['itemId']
            item_name = body['itemName']
            price = body['price']
            quantity = body['quantity']
            
            if DYNAMODB_AVAILABLE:
                # Update or create item in DynamoDB, handling reserved keyword 'items'
                table.update_item(
                    Key={'userId': user_id},
                    UpdateExpression='SET #items.#itemId = :item',
                    ExpressionAttributeNames={
                        '#items': 'items',
                        '#itemId': item_id
                    },
                    ExpressionAttributeValues={
                        ':item': {
                            'itemName': item_name,
                            'price': price,
                            'quantity': quantity
                        }
                    },
                    ReturnValues='UPDATED_NEW'
                )
                response_message = 'Item added to cart'
            else:
                # Simulate DynamoDB response for testing
                response_message = f'Simulated: Added {item_name} to cart for {user_id}'
            
            return {
                'statusCode': 200,
                'body': json.dumps({'message': response_message}),
                'headers': {'Content-Type': 'application/json'}
            }
        
        elif http_method == 'GET':
            if DYNAMODB_AVAILABLE:
                # Retrieve user's cart
                try:
                    response = table.get_item(Key={'userId': user_id})
                    items = response.get('Item', {}).get('items', {})
                    # Convert Decimal to JSON-serializable types
                    return {
                        'statusCode': 200,
                        'body': json.dumps({'items': items}, default=decimal_to_json),
                        'headers': {'Content-Type': 'application/json'}
                    }
                except ClientError as e:
                    return {
                        'statusCode': 500,
                        'body': json.dumps({'error': str(e)}),
                        'headers': {'Content-Type': 'application/json'}
                    }
            else:
                # Simulate cart retrieval
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'items': {
                            'book1': {'itemName': 'Book', 'price': 10, 'quantity': 1}
                        }
                    }),
                    'headers': {'Content-Type': 'application/json'}
                }
        
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Unsupported HTTP method'}),
                'headers': {'Content-Type': 'application/json'}
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }