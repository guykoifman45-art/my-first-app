"""Tests for requirements.txt manifest file.

This module tests that the requirements.txt file:
- Exists in the project root
- Contains all required Python dependencies
- Uses correct version specifiers
- Follows proper format conventions
"""

import os
import re
from pathlib import Path


class TestRequirementsFile:
    """Test suite for requirements.txt manifest file."""

    @staticmethod
    def _get_requirements_path():
        """Get the absolute path to requirements.txt."""
        current_dir = Path(__file__).parent.parent
        return current_dir / "requirements.txt"

    def test_requirements_file_exists(self):
        """Verify that requirements.txt exists in the project root."""
        req_path = self._get_requirements_path()
        assert req_path.exists(), f"requirements.txt not found at {req_path}"

    def test_requirements_is_file(self):
        """Verify that requirements.txt is a file, not a directory."""
        req_path = self._get_requirements_path()
        assert req_path.is_file(), f"{req_path} is not a file"

    def test_requirements_not_empty(self):
        """Verify that requirements.txt is not empty."""
        req_path = self._get_requirements_path()
        assert req_path.read_text().strip(), "requirements.txt is empty"

    def test_requirements_format_valid(self):
        """Verify that each line follows valid pip requirements format."""
        req_path = self._get_requirements_path()
        content = req_path.read_text()
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        # Valid format: package-name==version or package-name>=version or similar
        pkg_pattern = re.compile(r'^[a-zA-Z0-9\-_.]+[>=<!=]+[0-9.]+')

        for line in lines:
            assert pkg_pattern.match(line), f"Invalid package format: {line}"

    def test_requests_package_present(self):
        """Verify that requests>=2.25.0 is specified."""
        req_path = self._get_requirements_path()
        content = req_path.read_text()
        assert "requests>=2.25.0" in content, \
            "requests>=2.25.0 not found in requirements.txt"

    def test_pytest_package_present(self):
        """Verify that pytest>=6.0.0 is specified."""
        req_path = self._get_requirements_path()
        content = req_path.read_text()
        assert "pytest>=6.0.0" in content, \
            "pytest>=6.0.0 not found in requirements.txt"

    def test_pytest_cov_package_present(self):
        """Verify that pytest-cov>=2.12.0 is specified."""
        req_path = self._get_requirements_path()
        content = req_path.read_text()
        assert "pytest-cov>=2.12.0" in content, \
            "pytest-cov>=2.12.0 not found in requirements.txt"

    def test_black_package_present(self):
        """Verify that black>=21.0 is specified."""
        req_path = self._get_requirements_path()
        content = req_path.read_text()
        assert "black>=21.0" in content, \
            "black>=21.0 not found in requirements.txt"

    def test_flake8_package_present(self):
        """Verify that flake8>=3.9.0 is specified."""
        req_path = self._get_requirements_path()
        content = req_path.read_text()
        assert "flake8>=3.9.0" in content, \
            "flake8>=3.9.0 not found in requirements.txt"

    def test_no_local_path_dependencies(self):
        """Verify that no local path dependencies are present."""
        req_path = self._get_requirements_path()
        content = req_path.read_text()
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        for line in lines:
            assert not line.startswith('/'), \
                f"Local path dependency found: {line}"
            assert not line.startswith('./'), \
                f"Local path dependency found: {line}"
            assert not line.startswith('../'), \
                f"Local path dependency found: {line}"

    def test_no_git_urls(self):
        """Verify that no git URLs are present."""
        req_path = self._get_requirements_path()
        content = req_path.read_text()

        assert "git+" not in content, "Git URL dependencies found"
        assert "git@" not in content, "Git URL dependencies found"

    def test_no_comments_or_blank_lines_only(self):
        """Verify that all non-empty lines are valid package specifications."""
        req_path = self._get_requirements_path()
        content = req_path.read_text()
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Allow blank lines and comments
            if stripped and stripped.startswith('#'):
                continue
            # All other non-empty lines must be valid packages
            if stripped:
                pkg_pattern = re.compile(r'^[a-zA-Z0-9\-_.]+[>=<!=]+[0-9.]+')
                assert pkg_pattern.match(stripped), \
                    f"Line {i}: Invalid package format: {stripped}"

    def test_required_packages_count(self):
        """Verify that at least the 5 required packages are present."""
        req_path = self._get_requirements_path()
        content = req_path.read_text()
        lines = [line.strip() for line in content.split('\n')
                 if line.strip() and not line.strip().startswith('#')]

        assert len(lines) >= 5, \
            f"Expected at least 5 packages, found {len(lines)}"

    def test_python_version_compatibility(self):
        """Verify that the file can be used with Python 3.8+."""
        # This is a format check - requirements.txt should be
        # compatible with any Python 3.8+ pip version
        req_path = self._get_requirements_path()
        content = req_path.read_text()

        # Should not contain any Python version specifiers
        # that would exclude 3.8+
        lines = content.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('python_version'):
                # If present, should allow 3.8+
                assert '<3.8' not in stripped, \
                    "Requirements file excludes Python 3.8"

    def test_no_empty_package_names(self):
        """Verify that no packages have empty names."""
        req_path = self._get_requirements_path()
        content = req_path.read_text()
        lines = [line.strip() for line in content.split('\n')
                 if line.strip() and not line.strip().startswith('#')]

        for line in lines:
            # Extract package name (before any version specifier)
            match = re.match(r'^([a-zA-Z0-9\-_.]+)', line)
            assert match, f"Could not extract package name from: {line}"
            pkg_name = match.group(1)
            assert pkg_name, f"Empty package name in: {line}"
