"use client";

import { useParams, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";
import axios from "axios";

export default function AppointmentTabs() {
  const { id } = useParams();
  const router = useRouter();

  const [mounted, setMounted] = useState(false);
  const [appointmentName, setAppointmentName] = useState("");
  const [appointmentDate, setAppointmentDate] = useState("");
  const [activeTab, setActiveTab] = useState("Notes");
  const [noteId, setNoteId] = useState("");
  const [transcriptId, setTranscriptId] = useState("");
  const [markdownContent, setMarkdownContent] = useState("");
  const [fullTranscript, setFullTranscript] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notesLoading, setNotesLoading] = useState(false);

  const {
    transcript,
    listening,
    browserSupportsSpeechRecognition,
    finalTranscript,
    resetTranscript,
  } = useSpeechRecognition();

  const token =
    "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtJX3VfdkJ0RmdRZHNFdEhiSDFOZCJ9.eyJpc3MiOiJodHRwczovL2Rldi14N2p4MGJkNGs1dm4yanVyLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMjgzNjk0NzY0NDMxNzUwMDA1NSIsImF1ZCI6WyJodHRwczovL2Rldi14N2p4MGJkNGs1dm4yanVyLnVzLmF1dGgwLmNvbS9hcGkvdjIvIiwiaHR0cHM6Ly9kZXYteDdqeDBiZDRrNXZuMmp1ci51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzQzOTY3NTY0LCJleHAiOjE3NDM5NzQ3NjQsInNjb3BlIjoib3BlbmlkIGVtYWlsIiwiYXpwIjoiZ2VMSU5BZ3phRlVCV24xSmU2VDBMdkUzaDZNaXE0TTYifQ.ey3QsMPWiVHZaQWwTpdFYuhnJJXp473bssaVSVms_LAAijxCJGCQ36E9YcBQHMyusamV0gHSXQ7oowWsc7VgIJKbCnvnVI8NbvdFYDuv-F6BPjUjJMpXnILTEKh7uQohtjBVxkF8MaFO3Ehh-cafJg2CPzwZfDhqJ9JwV-8dZvLu_vC4yz12brtlTllMqqLdD_3LodoIOqF06SzBHFX7gXKPNi2WwyR5wXZwpkORjniY3Pc7Znd9f0_dQF-wXO_8WdT91Mf2UMgFTmVGaTFNPTGkvmwnd2IX1VCVwWf7hDBDUXFRs1dEKwpc1il8V-p4DGKFGqmPg0MjrR0uknUgvQ";

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!browserSupportsSpeechRecognition) {
    return (
      <div className="max-w-3xl mx-auto mt-10 p-6 bg-red-100 text-red-800 rounded">
        Your browser does not support speech recognition. Please use Chrome or
        Edge.
      </div>
    );
  }

  useEffect(() => {
    if (finalTranscript) {
      setFullTranscript((prev) => prev + " " + finalTranscript);
      resetTranscript();
    }
  }, [finalTranscript]);

  const fetchNoteData = async () => {
    if (!noteId) return;
    try {
      const response = await axios.get(
        `https://9b19-128-54-18-77.ngrok-free.app/note/${noteId}`,
        {
          headers: {
            "ngrok-skip-browser-warning": "true",
          },
        }
      );
      console.log(noteId);
      console.log(response.data.text);
      setMarkdownContent(response.data.text);
    } catch (err) {
      setError(err.response?.data?.message || "Error fetching note");
    }
  };

  const fetchTranscriptData = async () => {
    if (!transcriptId) return;
    try {
      setLoading(true);
      const response = await axios.get(
        `https://9b19-128-54-18-77.ngrok-free.app/transcript/${transcriptId}`,
        {
          headers: {
            "ngrok-skip-browser-warning": "true",
          },
        }
      );
      setFullTranscript(response.data.text);
    } catch (err) {
      setError(err.response?.data?.message || "Error fetching transcript");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === "Notes") {
      console.log("fetching notes (tab switch)");
      fetchNoteData();
    } else if (activeTab === "Transcript") {
      fetchTranscriptData();
    }
  }, [activeTab, noteId, transcriptId]);

  useEffect(() => {
    const fetchAppointmentData = async () => {
      try {
        setLoading(true);
        const response = await axios.get(
          `https://9b19-128-54-18-77.ngrok-free.app/appointments/${id}`,
          {
            headers: {
              "ngrok-skip-browser-warning": "true",
            },
          }
        );
        console.log(response.data.note_id);
        setAppointmentName(response.data.name);
        setAppointmentDate(response.data.date);
        setNoteId(response.data.note_id);
        setTranscriptId(response.data.transcript_id);
      } catch (err) {
        setError(err.response?.data?.message || "Error fetching appointment");
      } finally {
        setLoading(false);
      }
    };
    fetchAppointmentData();
  }, [id]);

  const sendTranscriptToBackend = async () => {
    try {
      // First call to save the transcript
      const response = await axios.post(
        "https://9b19-128-54-18-77.ngrok-free.app/transcript",
        {
          text: fullTranscript,
          appointment_id: id,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "ngrok-skip-browser-warning": "true",
          },
        }
      );

      // Make sure we have a note_id before proceeding
      if (!response.data.note_id) {
        console.error("No note_id received from backend");
        setError("Backend did not return a note ID");
        return;
      }

      setTranscriptId(response.data.transcript_id);

      // Second call to get the processed note
      const response1 = await axios.get(
        `https://9b19-128-54-18-77.ngrok-free.app/note/${response.data.note_id}`,
        {
          headers: {
            "ngrok-skip-browser-warning": "true",
          },
        }
      );

      // Log the response to see what's coming back
      console.log("Note content received:", response1.data);

      // Check if we got valid content
      if (response1.data && response1.data.text) {
        console.log("Setting markdown content:", response1.data.text);
        setMarkdownContent(response1.data.text);
      } else {
        console.warn("Received empty or invalid note content");
        setError("Received empty note from backend");
      }
    } catch (err) {
      console.error("Error in sendTranscriptToBackend:", err);
      setError(err.response?.data?.message || "Error saving transcript");
    }
  };

  const startRecording = () => {
    setActiveTab("Transcript");
    SpeechRecognition.startListening({ continuous: true, language: "en-US" });
  };

  const stopRecording = async () => {
    SpeechRecognition.stopListening();
    setNotesLoading(true);
    setActiveTab("Notes");
    await sendTranscriptToBackend();
    setNotesLoading(false);
  };

  const tabClass = (tab) =>
    `px-4 py-2 rounded-t-lg font-medium cursor-pointer transition-all duration-200 ${
      activeTab === tab
        ? "bg-[#568A97] text-white"
        : "bg-[#D5C6B9] text-gray-500 hover:bg-gray-300"
    }`;

  return (
    <div>
      <div className="max-w-3xl mx-auto mt-10">
        <h1 className="text-2xl font-semibold bg-[#568a97] rounded-lg text-center p-4">
          Appointment Tabs
        </h1>
        <div className="text-xs mb-4 text-gray-400 text-center">{id}</div>
        <h3 className="text-md text-center font-semibold">
          Name: <span className="font-normal">{appointmentName}</span>
        </h3>
        <h3 className="text-md text-center font-semibold mb-6">
          Date: <span className="font-normal">{appointmentDate}</span>
        </h3>
        <div className="flex space-x-2 border-b-4 mb-6 border-[#568A97]">
          <div
            onClick={() => setActiveTab("Notes")}
            className={tabClass("Notes")}
          >
            Notes
          </div>
          <div
            onClick={() => setActiveTab("Transcript")}
            className={tabClass("Transcript")}
          >
            Transcript
          </div>
        </div>
        <div className="p-6 bg-[#568A97] rounded-lg shadow-md">
          {activeTab === "Notes" &&
            (notesLoading ? (
              <div>Loading...</div>
            ) : (
              <div className="prose max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h1: ({ node, ...props }) => (
                      <h1 className="text-2xl font-bold my-4" {...props} />
                    ),
                    h2: ({ node, ...props }) => (
                      <h2 className="text-xl font-bold my-3" {...props} />
                    ),
                    p: ({ node, ...props }) => (
                      <p className="my-2" {...props} />
                    ),
                    ul: ({ node, ...props }) => (
                      <ul className="list-disc pl-5 my-2" {...props} />
                    ),
                    ol: ({ node, ...props }) => (
                      <ol className="list-decimal pl-5 my-2" {...props} />
                    ),
                    a: ({ node, children, ...props }) => (
                      <span className="flex items-center">
                        <span className="mr-2 font-bold">TODO: </span>
                        <a
                          {...props}
                          className="font-bold text-[#F0E9D8] underline hover:text-green-500"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {children}
                        </a>
                      </span>
                    ),
                  }}
                >
                  {markdownContent || "No notes yet."}
                </ReactMarkdown>
              </div>
            ))}
          {activeTab === "Transcript" && (
            <div className="p-4 bg-white rounded whitespace-pre-wrap text-grey-700">
              {listening && (
                <p className="text-sm text-green-600 mb-2">
                  Listening... Speak now.
                </p>
              )}
              {fullTranscript}
              <br />
              <span className="text-green-600">
                {listening && (transcript || "Listening...")}
              </span>
            </div>
          )}
        </div>
        <div className="flex space-x-4 mt-6">
          <button
            onClick={() => router.push("/")}
            className="mt-6 px-4 py-2 bg-[#947D9E] text-white rounded hover:bg-[#5d4e63] transition"
          >
            ← Back to Appointments
          </button>
          {!listening ? (
            <button
              onClick={startRecording}
              className="mt-6 px-4 py-2 bg-green-700 text-white rounded hover:bg-green-800 transition"
            >
              ⦿ Start Recording
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="mt-6 px-4 py-2 bg-red-700 text-white rounded hover:bg-red-800 transition"
            >
              ⬛ Stop Recording
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
