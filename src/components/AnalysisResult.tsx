import { CheckCircle, AlertCircle, Loader2 } from "lucide-react";

interface AnalysisResultProps {
  status: "pending" | "analyzing" | "completed" | "failed";
  // Backend can return string or structured object
  result: any | null;
  score?: number | null;
  renderUrl: string;
  referenceUrl?: string | null;
}

export function AnalysisResult({
  status,
  result,
  score,
  renderUrl,
  referenceUrl,
}: AnalysisResultProps) {
  if (status === "pending") return null;

  // Fallbacks/helpers
  const hasObj = (val: any) => val && typeof val === "object" && !Array.isArray(val);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Analysis Results</h2>

        {status === "analyzing" && (
          <div className="flex items-center text-blue-600">
            <Loader2 className="h-5 w-5 animate-spin mr-2" />
            <span className="text-sm font-medium">Analyzing...</span>
          </div>
        )}

        {status === "completed" && (
          <div className="flex items-center text-green-600">
            <CheckCircle className="h-5 w-5 mr-2" />
            <span className="text-sm font-medium">Complete</span>
          </div>
        )}

        {status === "failed" && (
          <div className="flex items-center text-red-600">
            <AlertCircle className="h-5 w-5 mr-2" />
            <span className="text-sm font-medium">Failed</span>
          </div>
        )}
      </div>

      {/* Images */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Your Render</h3>
          <img
            src={renderUrl}
            alt="Render"
            className="w-full rounded-lg border-2 border-gray-200"
          />
        </div>

        {referenceUrl && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Reference Image</h3>
            <img
              src={referenceUrl}
              alt="Reference"
              className="w-full rounded-lg border-2 border-gray-200"
            />
          </div>
        )}
      </div>

      {/* Completed view */}
      {status === "completed" && (
        <>
          {/* Overall score */}
          {score !== null && score !== undefined && (
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
              <div className="flex items-end gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">
                    Overall Quality Score
                  </p>
                  <div className="flex items-center gap-3">
                    <div className="text-5xl font-bold text-blue-600">
                      {score}
                    </div>
                    <div className="text-gray-500">/ 100</div>
                  </div>
                </div>
                <div className="flex-1">
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all ${
                        score >= 80
                          ? "bg-green-500"
                          : score >= 60
                          ? "bg-blue-500"
                          : score >= 40
                          ? "bg-yellow-500"
                          : "bg-red-500"
                      }`}
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Detailed Feedback (summary + sections + action steps) */}
          {result && (
            <div className="prose max-w-none">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                Detailed Feedback
              </h3>

              <div className="bg-gray-50 rounded-lg p-6 border border-gray-200 space-y-4">
                {/* Summary line */}
                {hasObj(result) && typeof result.summary === "string" && (
                  <p className="text-gray-700">{result.summary}</p>
                )}

                {/* Section grids when analysis is an object */}
                {hasObj(result) && hasObj(result.analysis) && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(result.analysis).map(([section, values]) => (
                      <div key={section} className="bg-white rounded-lg border p-4">
                        <h4 className="font-semibold mb-2 capitalize">{section}</h4>
                        <ul className="text-sm text-gray-700 space-y-1">
                          {Object.entries(values as Record<string, any>).map(([k, v]) => (
                            <li key={k}>
                              <span className="text-gray-500">{k}:</span>{" "}
                              {typeof v === "number" ? v.toString() : JSON.stringify(v)}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                )}

                {/* If result was simple text from backend */}
                {!hasObj(result) && typeof result === "string" && (
                  <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                    {result}
                  </p>
                )}

                {/* Actionable recommendations */}
                {hasObj(result) &&
                  Array.isArray(result.recommendations) &&
                  result.recommendations.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">Action Steps</h4>
                      <ul className="list-disc ml-6 text-gray-800 space-y-1">
                        {result.recommendations.map((r: string, i: number) => (
                          <li key={i}>{r}</li>
                        ))}
                      </ul>
                    </div>
                  )}
              </div>
            </div>
          )}
        </>
      )}

      {/* Failed message */}
      {status === "failed" && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">
            Analysis failed. Please try again or contact support if the issue persists.
          </p>
        </div>
      )}
    </div>
  );
}
