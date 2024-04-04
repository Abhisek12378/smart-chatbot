import { useState } from "react";
// import "./App.css";
import "./components/result.css"

export default function App() {
  const [result, setResult] = useState();
  const [question, setQuestion] = useState<string | undefined>("");
  const [file, setFile] = useState();
  const [timestamp, setTimestamp] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleQuestionChange = (event: any) => {
    setQuestion(event.target.value);
  };

  const handleFileChange = (event: any) => {
    setFile(event.target.files[0]);
    const newTimestamp = new Date().toISOString();
    setTimestamp(newTimestamp);
  };

  const handleSubmit = (event: any) => {
    event.preventDefault();
    setResult(undefined);
    setIsLoading(true);

    const formData = new FormData();

    if (file) {
      formData.append("file", file);
    }
    if (question) {
      formData.append("question", question);
    }
    formData.append("timestamp", timestamp);

    fetch(`${process.env.REACT_APP_BACKEND_URL}/predict`, {
           method: "POST",
           body: formData,
    })

      .then((response) => response.json())
      .then((data) => {
        setIsLoading(false);
        setResult(data.result);
        setQuestion("");
      })
      .catch((error) => {
        console.error("Error", error);
      });
  };

  return (
    <div className="appBlock">
      <form onSubmit={handleSubmit} className="form">
        <label className="questionLabel" htmlFor="question">
          Question:
        </label>
        <input
          className="questionInput"
          id="question"
          type="text"
          value={question}
          onChange={handleQuestionChange}
          placeholder="Ask your question here"
        />

        <br></br>
        <label className="fileLabel" htmlFor="file">
          Upload file:
        </label>

        <input
          type="file"
          id="file"
          name="file"
          accept=".csv, .pdf, .docx, .txt"
          onChange={handleFileChange}
          className="fileInput"
        />
        <br></br>
        <button
          className="submitBtn"
          type="submit"
          disabled={!file || !question}
        >
          Submit
        </button>
      </form>
      <div className="resultOutput">
        {isLoading ? (
          <p className="inProgress">...in progress...</p>
        ) : (
          result && <p>Result: {result}</p>
        )}
      </div>
    </div>
  );
}
