import os
from quart import Quart, request, jsonify
from quart_cors import cors
from searcher import LargeTextSearcher

app = Quart(__name__)
app = cors(app, allow_origin="*")

UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
async def upload_file():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.txt'):
        return jsonify({"error": "Invalid file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200

@app.route('/search', methods=['GET'])
async def search():
    filter_text = request.args.get('filter')
    if not filter_text:
        return jsonify({"error": "No filter provided"}), 400

    searcher = LargeTextSearcher(UPLOAD_FOLDER)
    results, time_taken, total_data_processed, total_results = await searcher.async_query_files(filter_text)

    if not results:
        return jsonify({
            "message": "No results found",
            "time_taken": f"{time_taken:.8f} s",
            "total_data_processed": total_data_processed,
            "total_results": total_results
        }), 404

    return jsonify({
        "results": results,
        "time_taken": f"{time_taken:.8f} s",
        "total_data_processed": total_data_processed,
        "total_results": total_results
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
