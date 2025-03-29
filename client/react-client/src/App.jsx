import { useState } from "react";
import axios from "axios";

export default function App() {
  const [file, setFile] = useState(null);
  const [password, setPassword] = useState("");
  const [fileUrl, setFileUrl] = useState(null);
  const [uuid, setUuid] = useState(null);
  const [downloadPassword, setDownloadPassword] = useState("");

  const handleFileChange = (e) => setFile(e.target.files[0]);
  const handlePasswordChange = (e) => setPassword(e.target.value);
  const handleDownloadPasswordChange = (e) => setDownloadPassword(e.target.value);

  const uploadFile = async () => {
    if (!file || !password) {
      return alert("Odaberite datoteku i unesite lozinku");
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("password", password);

    try {
      const res = await axios.post("http://localhost:5000/upload", formData);
      setUuid(res.data.file_path); 
      setFileUrl(`http://localhost:5000/get-file/${res.data.file_path}`);
    } catch (error) {
      console.error("Greška prilikom upload-a", error);
      alert("Neuspjelo slanje dokumenta");
    }
  };

  const downloadFile = async () => {
    if (!uuid) {
      return alert("Nema dostupnog UUID dokumenta");
    }
    try {
      const res = await axios.post(`http://localhost:5000/get-file/${uuid}`, { password: downloadPassword },{
        responseType: "blob", 
      });

      const blob = new Blob([res.data]);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = file ? file.name : "preuzeta_datoteka";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Greška pri preuzimanju", error);
      alert("Greška pri preuzimanju. Datoteka ne postoji ili je UUID netočan.");
    }
  };

  return (
    <div className="flex flex-col items-center p-6">
      <h1 className="text-2xl font-bold mb-4">Upload datoteke</h1>
      <input type="file" onChange={handleFileChange} className="mb-2" />
      <input
        type="password"
        placeholder="Lozinka"
        value={password}
        onChange={handlePasswordChange}
        className="mb-2 p-2 border"
      />
      <button onClick={uploadFile} className="px-4 py-2 bg-blue-500 text-white rounded">
        Upload
      </button>

      {fileUrl && (
        <div className="mt-4">
          <p>Datoteka je dostupna na:</p>
          <a href={fileUrl} target="_blank" rel="noopener noreferrer" className="text-blue-600">
            {fileUrl}
          </a>
        </div>
      )}

      {uuid && (
        <div className="mt-4">
          <h2 className="text-xl font-bold">Preuzmi datoteku</h2>
          <input
            type="password"
            placeholder="Unesi lozinku"
            value={downloadPassword}
            onChange={handleDownloadPasswordChange}
            className="mb-2 p-2 border"
          />
          <button onClick={downloadFile} className="px-4 py-2 bg-green-500 text-white rounded">
            Preuzmi
          </button>
        </div>
      )}
    </div>
  );
}
