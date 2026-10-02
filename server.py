"""
Web server for the Longest Common DNA Substring project.
Uses only Python standard library (http.server + json).
Serves the HTML frontend and handles API requests.
"""

import http.server
import json
import os
from main import longest_common_substring, longest_common_substring_optimized, validate_dna

PORT = 8000

class DNAHandler(http.server.SimpleHTTPRequestHandler):
    """Handles both static file serving and API requests."""

    def do_POST(self):
        if self.path == "/api/analyze":
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))

            s1 = data.get("s1", "").strip().upper()
            s2 = data.get("s2", "").strip().upper()

            # Validate
            if not validate_dna(s1) or not validate_dna(s2):
                self._json_response(400, {
                    "error": "Invalid input: DNA sequences may contain only A, C, G, T."
                })
                return

            # Run both algorithms
            sub_std, len_std = longest_common_substring(s1, s2)
            sub_opt, len_opt = longest_common_substring_optimized(s1, s2)

            # Build DP table for visualization
            dp_table = self._build_dp_table(s1, s2)

            self._json_response(200, {
                "s1": s1,
                "s2": s2,
                "substring": sub_std,
                "length": len_std,
                "optimized_substring": sub_opt,
                "optimized_length": len_opt,
                "dp_table": dp_table,
            })
        else:
            self.send_error(404, "Not Found")

    def _build_dp_table(self, s1, s2):
        """Build the full DP table for visualization."""
        if not s1 or not s2:
            return []
        n, m = len(s1), len(s2)
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = 0
        return dp

    def _json_response(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with http.server.HTTPServer(("", PORT), DNAHandler) as httpd:
        print(f"\n  DNA Substring Analyzer running at:")
        print(f"  >>  http://localhost:{PORT}")
        print(f"\n  Press Ctrl+C to stop.\n")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
