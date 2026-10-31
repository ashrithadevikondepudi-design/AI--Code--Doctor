"use client";

import { useState } from "react";
import Editor from "@monaco-editor/react";

type Issue = {
  type: string;
  message: string;
  line?: number;
};

type ReviewResult = {
  status: string;
  issues?: Issue[];
  message?: string;
};

type OptimizationResult = {
  status: string;
  suggestions?: string[];
  message?: string;
};

type SecurityResult = {
  status: string;
  issues?: Issue[];
  message?: string;
};

type ComplexityResult = {
  status: string;
  time_complexity?: string;
  space_complexity?: string;
  message?: string;
};

type ExplanationResult = {
  status: string;
  explanation?: string;
  suggestion?: string;
  source?: string;
  message?: string;
};

type ImprovementResult = {
  status: string;
  original_code?: string;
  improved_code?: string;
  message?: string;
  suggestions?: string[];
};

export default function Home() {
  const [code, setCode] = useState<string>(`def find_max(numbers):
    max_value = numbers[0]

    for number in numbers:
        if number > max_value:
            max_value = number

    return max_value`);

  const [review, setReview] = useState<ReviewResult | null>(null);
  const [optimization, setOptimization] =
    useState<OptimizationResult | null>(null);
  const [security, setSecurity] =
    useState<SecurityResult | null>(null);
  const [complexity, setComplexity] =
    useState<ComplexityResult | null>(null);
  const [explanation, setExplanation] =
    useState<ExplanationResult | null>(null);
  const [improvement, setImprovement] =
    useState<ImprovementResult | null>(null);

  const [analyzing, setAnalyzing] = useState(false);
  const [improving, setImproving] = useState(false);

  // =========================
  // ANALYZE CODE
  // =========================

  const analyzeCode = async () => {
    setAnalyzing(true);

    setReview(null);
    setOptimization(null);
    setSecurity(null);
    setComplexity(null);
    setExplanation(null);

    try {
      // -------------------------
      // CODE REVIEW
      // -------------------------

      const reviewResponse = await fetch(
        "http://127.0.0.1:8000/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            code: code,
          }),
        }
      );

      const reviewData = await reviewResponse.json();
      setReview(reviewData);

      // -------------------------
      // OPTIMIZATION
      // -------------------------

      const optimizationResponse = await fetch(
        "http://127.0.0.1:8000/optimize",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            code: code,
          }),
        }
      );

      const optimizationData =
        await optimizationResponse.json();

      setOptimization(optimizationData);

      // -------------------------
      // SECURITY
      // -------------------------

      const securityResponse = await fetch(
        "http://127.0.0.1:8000/security",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            code: code,
          }),
        }
      );

      const securityData =
        await securityResponse.json();

      setSecurity(securityData);

      // -------------------------
      // COMPLEXITY
      // -------------------------

      const complexityResponse = await fetch(
        "http://127.0.0.1:8000/complexity",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            code: code,
          }),
        }
      );

      const complexityData =
        await complexityResponse.json();

      setComplexity(complexityData);

      // -------------------------
      // AI EXPLANATION
      // -------------------------

      const explanationResponse = await fetch(
        "http://127.0.0.1:8000/explain",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            code: code,
          }),
        }
      );

      const explanationData =
        await explanationResponse.json();

      setExplanation(explanationData);
    } catch (error) {
      console.error("Analysis error:", error);

      setReview({
        status: "error",
        message:
          "Could not connect to FastAPI backend.",
      });
    } finally {
      setAnalyzing(false);
    }
  };

  // =========================
  // IMPROVE CODE
  // =========================

  const improveCode = async () => {
    setImproving(true);
    setImprovement(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/improve",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            code: code,
          }),
        }
      );

      const data = await response.json();

      setImprovement(data);
    } catch (error) {
      console.error("Improvement error:", error);

      setImprovement({
        status: "error",
        message:
          "Could not connect to FastAPI backend.",
      });
    } finally {
      setImproving(false);
    }
  };

  // =========================
  // APPLY IMPROVED CODE
  // =========================

  const applyImprovedCode = () => {
    if (improvement?.improved_code) {
      setCode(improvement.improved_code);
    }
  };

  // =========================
  // COPY IMPROVED CODE
  // =========================

  const copyImprovedCode = async () => {
    if (improvement?.improved_code) {
      await navigator.clipboard.writeText(
        improvement.improved_code
      );
    }
  };

  return (
    <main className="min-h-screen bg-gray-950 text-white p-6">

      {/* ================= HEADER ================= */}

      <div className="mb-6">
        <h1 className="text-3xl font-bold">
          🩺 AI Code Doctor
        </h1>

        <p className="text-gray-400 mt-1">
          AI-powered code review and optimization assistant
        </p>
      </div>

      {/* ================= MAIN LAYOUT ================= */}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* ================= LEFT SIDE ================= */}

        <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">

          <h2 className="text-xl font-semibold mb-4">
            💻 Code Editor
          </h2>

          <div className="border border-gray-700 rounded-lg overflow-hidden">

            <Editor
              height="500px"
              defaultLanguage="python"
              theme="vs-dark"
              value={code}
              onChange={(value) =>
                setCode(value || "")
              }
              options={{
                minimap: {
                  enabled: false,
                },
                fontSize: 14,
                automaticLayout: true,
                scrollBeyondLastLine: false,
              }}
            />

          </div>

          {/* BUTTONS */}

          <div className="flex gap-3 mt-4">

            <button
              onClick={analyzeCode}
              disabled={analyzing}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 px-4 py-3 rounded-lg font-semibold transition"
            >
              {analyzing
                ? "Analyzing..."
                : "🔍 Analyze Code"}
            </button>

            <button
              onClick={improveCode}
              disabled={improving}
              className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 px-4 py-3 rounded-lg font-semibold transition"
            >
              {improving
                ? "Improving..."
                : "✨ Improve Code"}
            </button>

          </div>
        </div>

        {/* ================= RIGHT SIDE ================= */}

        <div className="space-y-4">

          {/* ================= CODE REVIEW ================= */}

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">

            <h2 className="text-lg font-semibold mb-3">
              🔍 Code Review
            </h2>

            {!review && (
              <p className="text-gray-500">
                Run analysis to see code review.
              </p>
            )}

            {/* ISSUES FOUND */}

            {review?.status === "issues_found" &&
              review.issues &&
              review.issues.length > 0 && (

                <div className="space-y-3">

                  {review.issues.map(
                    (issue, index) => (

                      <div
                        key={index}
                        className="bg-gray-800 rounded-lg p-3"
                      >

                        <p className="text-yellow-400 font-semibold">
                          {issue.type}
                        </p>

                        <p className="text-gray-300 mt-1">
                          {issue.message}
                        </p>

                        {issue.line && (
                          <p className="text-gray-500 text-sm mt-1">
                            Line {issue.line}
                          </p>
                        )}

                      </div>

                    )
                  )}

                </div>

              )}

            {/* GOOD CODE */}

            {review?.status === "good" && (

              <div className="bg-gray-800 rounded-lg p-3">

                <p className="text-green-400 font-semibold">
                  ✅ No obvious issues detected.
                </p>

                {review.message && (
                  <p className="text-gray-400 mt-2">
                    {review.message}
                  </p>
                )}

              </div>

            )}

            {/* ERROR */}

            {review?.status === "error" && (

              <p className="text-red-400">
                ❌ {review.message}
              </p>

            )}

          </div>

          {/* ================= OPTIMIZATION ================= */}

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">

            <h2 className="text-lg font-semibold mb-3">
              ⚡ Optimization
            </h2>

            {!optimization && (
              <p className="text-gray-500">
                Optimization suggestions will appear here.
              </p>
            )}

            {optimization?.message && (
              <p className="text-gray-300 mb-3">
                {optimization.message}
              </p>
            )}

            {optimization?.suggestions &&
              optimization.suggestions.length > 0 && (

                <ul className="list-disc ml-5 space-y-2 text-gray-300">

                  {optimization.suggestions.map(
                    (suggestion, index) => (
                      <li key={index}>
                        {suggestion}
                      </li>
                    )
                  )}

                </ul>

              )}

            {optimization?.suggestions &&
              optimization.suggestions.length === 0 && (

                <p className="text-green-400">
                  ✅ No obvious optimization suggestions.
                </p>

              )}

          </div>

          {/* ================= SECURITY ================= */}

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">

            <h2 className="text-lg font-semibold mb-3">
              🔐 Security
            </h2>

            {!security && (
              <p className="text-gray-500">
                Security analysis will appear here.
              </p>
            )}

            {security?.issues &&
              security.issues.length > 0 && (

                <div className="space-y-3">

                  {security.issues.map(
                    (issue, index) => (

                      <div
                        key={index}
                        className="bg-gray-800 rounded-lg p-3"
                      >

                        <p className="text-red-400 font-semibold">
                          {issue.type}
                        </p>

                        <p className="text-gray-300 mt-1">
                          {issue.message}
                        </p>

                        {issue.line && (
                          <p className="text-gray-500 text-sm mt-1">
                            Line {issue.line}
                          </p>
                        )}

                      </div>

                    )
                  )}

                </div>

              )}

            {security?.issues &&
              security.issues.length === 0 && (

                <p className="text-green-400">
                  ✅ No obvious security risks detected.
                </p>

              )}

            {security?.message && (
              <p className="text-gray-300">
                {security.message}
              </p>
            )}

          </div>

          {/* ================= COMPLEXITY ================= */}

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">

            <h2 className="text-lg font-semibold mb-3">
              📊 Complexity Analysis
            </h2>

            {!complexity && (
              <p className="text-gray-500">
                Complexity analysis will appear here.
              </p>
            )}

            {complexity && (

              <div className="space-y-2">

                <div className="flex justify-between bg-gray-800 rounded-lg p-3">

                  <span className="text-gray-400">
                    Time Complexity
                  </span>

                  <span className="text-blue-400 font-semibold">
                    {complexity.time_complexity ||
                      "Not available"}
                  </span>

                </div>

                <div className="flex justify-between bg-gray-800 rounded-lg p-3">

                  <span className="text-gray-400">
                    Space Complexity
                  </span>

                  <span className="text-purple-400 font-semibold">
                    {complexity.space_complexity ||
                      "Not available"}
                  </span>

                </div>

                {complexity.message && (
                  <p className="text-gray-300 mt-2">
                    {complexity.message}
                  </p>
                )}

              </div>

            )}

          </div>

          {/* ================= AI EXPLANATION ================= */}

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">

            <h2 className="text-lg font-semibold mb-3">
              🤖 AI Explanation
            </h2>

            {!explanation && (
              <p className="text-gray-500">
                AI explanation will appear here.
              </p>
            )}

            {explanation?.explanation && (

              <div>

                <p className="text-gray-300 leading-relaxed">
                  {explanation.explanation}
                </p>

                {explanation.suggestion && (

                  <div className="mt-3 bg-gray-800 rounded-lg p-3">

                    <p className="text-purple-400 font-semibold">
                      💡 Suggestion
                    </p>

                    <p className="text-gray-300 mt-1">
                      {explanation.suggestion}
                    </p>

                  </div>

                )}

                {explanation.source && (
                  <p className="text-gray-500 text-sm mt-3">
                    Source: {explanation.source}
                  </p>
                )}

              </div>

            )}

            {explanation?.message &&
              !explanation.explanation && (

                <p className="text-gray-300">
                  {explanation.message}
                </p>

              )}

          </div>

          {/* ================= IMPROVED CODE ================= */}

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">

            <h2 className="text-lg font-semibold mb-3">
              ✨ Improved Code
            </h2>

            {!improvement && (
              <p className="text-gray-500">
                Click "Improve Code" to generate an improved version.
              </p>
            )}

            {/* SUCCESS */}

            {improvement?.status === "success" && (

              <div>

                {improvement.message && (
                  <p className="text-gray-300 mb-3">
                    {improvement.message}
                  </p>
                )}

                {/* SUGGESTIONS */}

                {improvement.suggestions &&
                  improvement.suggestions.length > 0 && (

                    <div className="mb-4">

                      <p className="text-purple-400 font-semibold mb-2">
                        💡 Suggestions
                      </p>

                      <ul className="list-disc ml-5 space-y-1 text-gray-300">

                        {improvement.suggestions.map(
                          (suggestion, index) => (
                            <li key={index}>
                              {suggestion}
                            </li>
                          )
                        )}

                      </ul>

                    </div>

                  )}

                {/* IMPROVED CODE */}

                {improvement.improved_code && (

                  <>

                    <p className="text-green-400 font-semibold mb-2">
                      Improved Code
                    </p>

                    <pre className="bg-gray-950 border border-gray-700 rounded-lg p-4 overflow-x-auto text-sm text-gray-200">
                      {improvement.improved_code}
                    </pre>

                    <div className="flex gap-3 mt-3">

                      <button
                        onClick={copyImprovedCode}
                        className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg transition"
                      >
                        📋 Copy
                      </button>

                      <button
                        onClick={applyImprovedCode}
                        className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg transition"
                      >
                        ✅ Apply to Editor
                      </button>

                    </div>

                  </>

                )}

              </div>

            )}

            {/* NO CHANGES */}

            {improvement?.status === "no_changes" && (

              <div>

                <p className="text-green-400">
                  ℹ️{" "}
                  {improvement.message ||
                    "No obvious improvements found."}
                </p>

                {improvement.improved_code && (
                  <pre className="bg-gray-950 border border-gray-700 rounded-lg p-4 overflow-x-auto text-sm text-gray-200 mt-3">
                    {improvement.improved_code}
                  </pre>
                )}

              </div>

            )}

            {/* ERROR */}

            {improvement?.status === "error" && (

              <p className="text-red-400">
                ❌{" "}
                {improvement.message ||
                  "Could not improve the code."}
              </p>

            )}

          </div>

        </div>
      </div>
    </main>
  );
}