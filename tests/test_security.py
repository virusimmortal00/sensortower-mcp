#!/usr/bin/env python3
"""
Security testing script for sensortower-mcp.
Validates security best practices and checks for common vulnerabilities.
"""

import os
import json
import subprocess
import asyncio
import httpx
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

class SecurityTester:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []
    
    def log_issue(self, category: str, issue: str, severity: str = "HIGH"):
        self.issues.append({"category": category, "issue": issue, "severity": severity})
        print(f"🔴 {severity}: {category} - {issue}")
    
    def log_warning(self, category: str, warning: str):
        self.warnings.append({"category": category, "warning": warning})
        print(f"🟡 WARNING: {category} - {warning}")
    
    def log_pass(self, category: str, check: str):
        self.passed.append({"category": category, "check": check})
        print(f"🟢 PASS: {category} - {check}")
    
    def run_command(self, cmd: List[str]) -> Tuple[bool, str, str]:
        """Run command and return success, stdout, stderr"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout"
        except Exception as e:
            return False, "", str(e)

    def check_dockerfile_security(self):
        """Check Dockerfile for security best practices"""
        print("\n📋 Checking Dockerfile Security...")
        
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        if not dockerfile_path.exists():
            self.log_warning("Dockerfile", "Dockerfile not found")
            return
        
        with open(dockerfile_path, "r") as f:
            content = f.read()
        
        # Check for non-root user
        if "USER " in content and "USER root" not in content:
            self.log_pass("Dockerfile", "Non-root user configured")
        else:
            self.log_issue("Dockerfile", "Container runs as root user", "MEDIUM")
        
        # Check for specific version pinning
        if re.search(r"FROM.*:[\d.]+", content):
            self.log_pass("Dockerfile", "Base image version pinned")
        else:
            self.log_warning("Dockerfile", "Base image version not pinned (using latest)")
        
        # Check for minimal base image
        if "slim" in content or "alpine" in content:
            self.log_pass("Dockerfile", "Minimal base image used")
        else:
            self.log_warning("Dockerfile", "Consider using slim/alpine base image")
        
        # Check for unnecessary packages
        if "apt-get update" in content:
            if "rm -rf /var/lib/apt/lists/*" in content:
                self.log_pass("Dockerfile", "Package cache cleaned")
            else:
                self.log_warning("Dockerfile", "Package cache not cleaned")
        
        # Check for secrets
        secret_patterns = [
            r"PASSWORD\s*=\s*['\"][^'\"]+['\"]",
            r"SECRET\s*=\s*['\"][^'\"]+['\"]",
            r"TOKEN\s*=\s*['\"][^'\"]+['\"]",
            r"API_KEY\s*=\s*['\"][^'\"]+['\"]"
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.log_issue("Dockerfile", f"Potential hardcoded secret found: {pattern}")
        
        if not any(re.search(p, content, re.IGNORECASE) for p in secret_patterns):
            self.log_pass("Dockerfile", "No hardcoded secrets found")

    def check_source_code_security(self):
        """Check source code for security issues"""
        print("\n🔍 Checking Source Code Security...")
        
        main_path = Path(__file__).parent.parent / "main.py"
        if not main_path.exists():
            self.log_warning("Source Code", "main.py not found")
            return
        
        with open(main_path, "r") as f:
            content = f.read()
        
        # Check for hardcoded secrets
        secret_patterns = [
            r"['\"][a-zA-Z0-9]{32,}['\"]",  # Potential API keys
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]"
        ]
        
        for pattern in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if "test" not in match.lower() and "example" not in match.lower():
                    self.log_issue("Source Code", f"Potential hardcoded secret: {match}")
        
        # Check for SQL injection protection (if applicable)
        if "sql" in content.lower() or "query" in content.lower():
            if "parameterized" in content or "?" in content:
                self.log_pass("Source Code", "Parameterized queries used")
            else:
                self.log_warning("Source Code", "Ensure SQL queries are parameterized")
        
        # Check for input validation
        if "httpx" in content or "requests" in content:
            if "timeout" in content:
                self.log_pass("Source Code", "HTTP timeouts configured")
            else:
                self.log_warning("Source Code", "HTTP timeouts not explicitly configured")
        
        # Check for environment variable usage
        if "os.getenv" in content or "os.environ" in content:
            self.log_pass("Source Code", "Environment variables used for configuration")
        
        # Check for exception handling
        if "try:" in content and "except" in content:
            self.log_pass("Source Code", "Exception handling implemented")
        else:
            self.log_warning("Source Code", "Limited exception handling found")

    def check_dependencies_security(self):
        """Check for vulnerable dependencies"""
        print("\n📦 Checking Dependencies Security...")
        
        # Check requirements.txt
        req_path = Path(__file__).parent.parent / "requirements.txt"
        if req_path.exists():
            success, stdout, stderr = self.run_command(["pip", "install", "safety"])
            if success:
                success, stdout, stderr = self.run_command(["safety", "check", "-r", str(req_path)])
                if success and "No known security vulnerabilities found" in stdout:
                    self.log_pass("Dependencies", "No known vulnerabilities in requirements.txt")
                elif "vulnerabilities found" in stdout:
                    self.log_issue("Dependencies", f"Vulnerabilities found: {stdout}")
                else:
                    self.log_warning("Dependencies", "Could not check vulnerabilities with safety")
            else:
                self.log_warning("Dependencies", "Safety tool not available for vulnerability checking")
        
        # Check pyproject.toml
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "r") as f:
                content = f.read()
            
            # Check for version pinning
            if ">=" in content and "==" not in content:
                self.log_warning("Dependencies", "Dependencies not pinned to specific versions")
            else:
                self.log_pass("Dependencies", "Dependencies properly versioned")

    async def check_runtime_security(self):
        """Check runtime security"""
        print("\n🏃 Checking Runtime Security...")
        
        # Test with invalid token
        env = os.environ.copy()
        env["SENSOR_TOWER_API_TOKEN"] = "invalid_token_123"
        
        # Get path to main.py relative to tests directory
        main_path = Path(__file__).parent.parent / "main.py"
        
        try:
            process = subprocess.Popen(
                ["python", str(main_path), "--transport", "http", "--port", "8669"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            await asyncio.sleep(3)
            
            # Test unauthorized access
            async with httpx.AsyncClient() as client:
                try:
                    # Try to access without proper authentication
                    response = await client.post(
                        "http://localhost:8669/mcp/tools/invoke",
                        json={
                            "tool": "search_entities",
                            "arguments": {
                                "os": "ios",
                                "entity_type": "app",
                                "term": "test"
                            }
                        },
                        timeout=5
                    )
                    
                    if response.status_code == 401 or response.status_code == 403:
                        self.log_pass("Runtime", "Proper authentication required")
                    elif response.status_code >= 400:
                        self.log_pass("Runtime", "Invalid requests properly rejected")
                    else:
                        self.log_warning("Runtime", "Authentication validation unclear")
                
                except Exception as e:
                    self.log_warning("Runtime", f"Could not test authentication: {e}")
                
                # Test health endpoint (should be accessible)
                try:
                    response = await client.get("http://localhost:8669/health", timeout=5)
                    if response.status_code == 200:
                        self.log_pass("Runtime", "Health endpoint accessible")
                    else:
                        self.log_warning("Runtime", "Health endpoint not accessible")
                except Exception as e:
                    self.log_warning("Runtime", f"Health endpoint error: {e}")
            
            process.terminate()
            process.wait(timeout=5)
            
        except Exception as e:
            self.log_warning("Runtime", f"Could not test runtime security: {e}")

    def check_docker_security(self):
        """Check Docker image security"""
        print("\n🐳 Checking Docker Security...")
        
        # Check if image exists
        success, stdout, stderr = self.run_command(["docker", "images", "bobbysayers492/sensortower-mcp", "--format", "{{.Repository}}:{{.Tag}}"])
        if not success or not stdout.strip():
            self.log_warning("Docker", "Docker image not found locally")
            return
        
        # Inspect image for security
        success, stdout, stderr = self.run_command(["docker", "inspect", "bobbysayers492/sensortower-mcp:latest"])
        if success:
            try:
                data = json.loads(stdout)[0]
                config = data.get("Config", {})
                
                # Check user
                user = config.get("User", "")
                if user and user != "root" and user != "0":
                    self.log_pass("Docker", f"Non-root user: {user}")
                else:
                    self.log_issue("Docker", "Container runs as root", "MEDIUM")
                
                # Check exposed ports
                exposed_ports = config.get("ExposedPorts", {})
                if exposed_ports:
                    ports = list(exposed_ports.keys())
                    if len(ports) == 1 and "8666" in ports[0]:
                        self.log_pass("Docker", "Only necessary port exposed")
                    else:
                        self.log_warning("Docker", f"Multiple ports exposed: {ports}")
                
                # Check environment variables for secrets
                env_vars = config.get("Env", [])
                for env_var in env_vars:
                    if any(secret in env_var.upper() for secret in ["PASSWORD", "SECRET", "TOKEN", "KEY"]):
                        if "=" in env_var and len(env_var.split("=")[1]) > 10:
                            self.log_issue("Docker", f"Potential secret in environment: {env_var.split('=')[0]}")
                
            except json.JSONDecodeError:
                self.log_warning("Docker", "Could not parse docker inspect output")
        
        # Security scanning with Trivy (if available)
        success, stdout, stderr = self.run_command(["trivy", "--version"])
        if success:
            success, stdout, stderr = self.run_command([
                "trivy", "image", "--severity", "HIGH,CRITICAL", 
                "--format", "json", "bobbysayers492/sensortower-mcp:latest"
            ])
            if success:
                try:
                    data = json.loads(stdout)
                    vulnerabilities = []
                    for result in data.get("Results", []):
                        for vuln in result.get("Vulnerabilities", []):
                            if vuln.get("Severity") in ["HIGH", "CRITICAL"]:
                                vulnerabilities.append(vuln)
                    
                    if not vulnerabilities:
                        self.log_pass("Docker", "No high/critical vulnerabilities found")
                    else:
                        self.log_issue("Docker", f"Found {len(vulnerabilities)} high/critical vulnerabilities")
                        for vuln in vulnerabilities[:5]:  # Show first 5
                            self.log_issue("Docker", f"  {vuln.get('VulnerabilityID')}: {vuln.get('Title', 'N/A')}", "INFO")
                
                except json.JSONDecodeError:
                    self.log_warning("Docker", "Could not parse Trivy output")
            else:
                self.log_warning("Docker", "Trivy scan failed")
        else:
            self.log_warning("Docker", "Trivy not available for vulnerability scanning")
            print("  Install with: docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy --version")

    def check_network_security(self):
        """Check network security configurations"""
        print("\n🌐 Checking Network Security...")
        
        # Check docker-compose.yml for network configuration
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        if compose_path.exists():
            with open(compose_path, "r") as f:
                content = f.read()
            
            # Check for custom networks
            if "networks:" in content:
                self.log_pass("Network", "Custom networks configured")
            else:
                self.log_warning("Network", "Using default Docker network")
            
            # Check for unnecessary port exposures
            port_pattern = r"ports:\s*\n\s*-\s*['\"]?(\d+):"
            ports = re.findall(port_pattern, content)
            if len(ports) <= 2:  # App port + maybe nginx
                self.log_pass("Network", "Minimal port exposure")
            else:
                self.log_warning("Network", f"Multiple ports exposed: {ports}")
            
            # Check for TLS/SSL configuration
            if "ssl" in content.lower() or "tls" in content.lower() or "443" in content:
                self.log_pass("Network", "TLS/SSL configuration present")
            else:
                self.log_warning("Network", "No TLS/SSL configuration found")

    def check_configuration_security(self):
        """Check configuration security"""
        print("\n⚙️  Checking Configuration Security...")
        
        project_root = Path(__file__).parent.parent
        
        # Check for .env files
        env_path = project_root / ".env"
        if env_path.exists():
            self.log_warning("Configuration", ".env file present - ensure it's in .gitignore")
            with open(env_path, "r") as f:
                content = f.read()
            if "SENSOR_TOWER_API_TOKEN" in content:
                self.log_issue("Configuration", "API token in .env file - use secure secret management")
        
        # Check .gitignore
        gitignore_path = project_root / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                gitignore = f.read()
            if ".env" in gitignore:
                self.log_pass("Configuration", ".env files excluded from git")
            else:
                self.log_warning("Configuration", ".env files not in .gitignore")
        
        # Check for production configuration
        config_files = ["nginx.conf", "docker-compose.yml", "docker-compose.prod.yml"]
        for config_file in config_files:
            config_path = project_root / config_file
            if config_path.exists():
                with open(config_path, "r") as f:
                    content = f.read()
                
                # Check for development/debug settings
                if "debug" in content.lower() and "true" in content.lower():
                    self.log_warning("Configuration", f"Debug mode found in {config_file}")
                
                # Check for secure headers (nginx)
                if config_file == "nginx.conf":
                    security_headers = [
                        "X-Frame-Options",
                        "X-Content-Type-Options",
                        "X-XSS-Protection",
                        "Strict-Transport-Security"
                    ]
                    missing_headers = []
                    for header in security_headers:
                        if header not in content:
                            missing_headers.append(header)
                    
                    if not missing_headers:
                        self.log_pass("Configuration", "Security headers configured in nginx")
                    else:
                        self.log_warning("Configuration", f"Missing security headers: {missing_headers}")

    def generate_report(self):
        """Generate security report"""
        print("\n" + "="*60)
        print("🔒 SECURITY REPORT")
        print("="*60)
        
        print(f"\n✅ PASSED CHECKS: {len(self.passed)}")
        for item in self.passed:
            print(f"  ✓ {item['category']}: {item['check']}")
        
        print(f"\n⚠️  WARNINGS: {len(self.warnings)}")
        for item in self.warnings:
            print(f"  ⚠ {item['category']}: {item['warning']}")
        
        print(f"\n🚨 SECURITY ISSUES: {len(self.issues)}")
        for item in self.issues:
            print(f"  🚨 {item['severity']} - {item['category']}: {item['issue']}")
        
        # Security score
        total_checks = len(self.passed) + len(self.warnings) + len(self.issues)
        if total_checks > 0:
            score = (len(self.passed) / total_checks) * 100
            print(f"\n📊 SECURITY SCORE: {score:.1f}%")
            
            if score >= 90:
                print("🟢 EXCELLENT - Ready for production")
            elif score >= 80:
                print("🟡 GOOD - Address warnings before production")
            elif score >= 70:
                print("🟠 FAIR - Address issues before production")
            else:
                print("🔴 POOR - Significant security concerns")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if len(self.issues) > 0:
            print("  1. Address all HIGH severity security issues")
        if len(self.warnings) > 0:
            print("  2. Review and address security warnings")
        print("  3. Run regular security scans with tools like Trivy")
        print("  4. Keep dependencies updated")
        print("  5. Use secrets management in production")
        print("  6. Enable TLS/SSL for production deployments")
        print("  7. Implement monitoring and alerting")

async def main():
    """Main security testing function"""
    print("🛡️  Sensor Tower MCP Security Testing")
    print("="*50)
    
    tester = SecurityTester()
    
    # Run all security checks
    tester.check_dockerfile_security()
    tester.check_source_code_security()
    tester.check_dependencies_security()
    await tester.check_runtime_security()
    tester.check_docker_security()
    tester.check_network_security()
    tester.check_configuration_security()
    
    # Generate report
    tester.generate_report()
    
    # Exit with appropriate code
    if any(issue["severity"] == "HIGH" for issue in tester.issues):
        print(f"\n🔴 Security testing failed due to HIGH severity issues")
        exit(1)
    elif len(tester.issues) > 0:
        print(f"\n🟡 Security testing completed with issues to address")
        exit(0)
    else:
        print(f"\n🟢 Security testing passed!")
        exit(0)

if __name__ == "__main__":
    asyncio.run(main()) 