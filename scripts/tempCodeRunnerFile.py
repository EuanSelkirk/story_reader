    # batch_input_file = client.files.create(
    #     file=open(output_path, "rb"),
    #     purpose="batch"
    # )

    # batch_input_file_id = batch_input_file.id

    # batch = client.batches.create(
    #     input_file_id=batch_input_file_id,
    #     endpoint="/v1/chat/completions",
    #     completion_window="24h"
    # )

    # batch_id = batch.id

    # # Poll for batch status until it is complete
    # while True:
    #     batch_status = client.batches.retrieve(batch_id)
    #     if batch_status.status == 'completed':
    #         break
    #     print(f"Batch {batch_id} is still processing. Checking again in 60 seconds...")
    #     time.sleep(60)  # Wait for 60 seconds before checking again

    # # Retrieve the result file once the batch is complete
    # batch_files = client.files.list(purpose="batch_result")
    # result_file = next((file for file in batch_files['data'] if file['batch_id'] == batch_id), None)
    
    # if result_file:
    #     result_file_id = result_file['id']
    #     result = client.files.download(result_file_id)
    
    #     # Save the result to a file
    #     result_output_path = f"{jsonl_story_path}/{name_seed}_results.jsonl"
    #     with open(result_output_path, "wb") as result_file:
    #         result_file.write(result)

    #     print(f"Batch {batch_id} is complete. Results saved to {result_output_path}")
    # else:
    #     print(f"Result file for batch {batch_id} not found.")