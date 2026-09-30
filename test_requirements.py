"""Tests for requirements.txt file validation."""

import os
import re
from pathlib import Path


class TestRequirementsFile:
    """Test suite for requirements.txt file."""

    @staticmethod
    def get_requirements_path():
        """Get the absolute path to requirements.txt."""
        base_dir = Path(__file__).parent
        return base_dir / "requirements.txt"

    def test_requirements_file_exists(self):
        """Test that requirements.txt file exists."""
        req_path = self.get_requirements_path()
        assert req_path.exists(), f"requirements.txt not found at {req_path}"

    def test_requirements_file_is_readable(self):
        """Test that requirements.txt file can be read."""
        req_path = self.get_requirements_path()
        with open(req_path, "r") as f:
            content = f.read()
        assert content, "requirements.txt is empty"

    def test_requirements_format(self):
        """Test that each line in requirements.txt follows the correct format."""
        req_path = self.get_requirements_path()
        with open(req_path, "r") as f:
            lines = f.readlines()

        # Pattern: package-name==version or package-name>=version
        pattern = re.compile(r"^[a-zA-Z0-9\-_.]+[><=!]+[\d.]+.*$")

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip empty lines and comments
            if not stripped or stripped.startswith("#"):
                continue
            assert pattern.match(stripped), (
                f"Line {line_num} '{stripped}' does not match "
                "package-name==version or package-name>=version format"
            )

    def test_requests_package_present(self):
        """Test that requests package with correct version is present."""
        req_path = self.get_requirements_path()
        with open(req_path, "r") as f:
            content = f.read()

        assert "requests" in content, "requests package not found in requirements.txt"
        # Should have either == or >= version specifier
        assert any(
            line.strip().startswith("requests")
            for line in content.split("\n")
            if "requests" in line
        ), "requests package malformed"

        # Verify version constraint is >= 2.25.0 or ==
        for line in content.split("\n"):
            if line.strip().startswith("requests"):
                assert (
                    "2.25" in line or "2.26" in line or "3." in line
                ) or ">=2.25" in line, (
                    f"requests version does not meet spec (>=2.25.0): {line}"
                )

    def test_pytest_package_present(self):
        """Test that pytest package with correct version is present."""
        req_path = self.get_requirements_path()
        with open(req_path, "r") as f:
            content = f.read()

        assert "pytest" in content, "pytest package not found in requirements.txt"
        # Find pytest line (but not pytest-cov)
        pytest_lines = [
            line.strip()
            for line in content.split("\n")
            if line.strip().startswith("pytest") and "pytest-cov" not in line
        ]
        assert len(pytest_lines) > 0, "pytest package malformed or not found"

        # Verify version constraint is >= 6.0.0 or ==
        for line in pytest_lines:
            assert (
                "6." in line or "7." in line or "8." in line
            ) or ">=6" in line, (
                f"pytest version does not meet spec (>=6.0.0): {line}"
            )

    def test_pytest_cov_package_present(self):
        """Test that pytest-cov package with correct version is present."""
        req_path = self.get_requirements_path()
        with open(req_path, "r") as f:
            content = f.read()

        assert "pytest-cov" in content, "pytest-cov package not found in requirements.txt"

        # Find pytest-cov line
        pytest_cov_lines = [
            line.strip()
            for line in content.split("\n")
            if "pytest-cov" in line
        ]
        assert len(pytest_cov_lines) > 0, "pytest-cov package malformed"

        # Verify version constraint is >= 2.12.0 or ==
        for line in pytest_cov_lines:
            assert (
                "2.12" in line or "2.13" in line or "3." in line
            ) or ">=2.12" in line, (
                f"pytest-cov version does not meet spec (>=2.12.0): {line}"
            )

    def test_black_package_present(self):
        """Test that black package with correct version is present."""
        req_path = self.get_requirements_path()
        with open(req_path, "r") as f:
            content = f.read()

        assert "black" in content, "black package not found in requirements.txt"

        # Find black line
        black_lines = [
            line.strip()
            for line in content.split("\n")
            if line.strip().startswith("black")
        ]
        assert len(black_lines) > 0, "black package malformed"

        # Verify version constraint is >= 21.0 or ==
        for line in black_lines:
            assert (
                "21." in line or "22." in line or "23." in line or "24." in line
            ) or ">=21" in line, (
                f"black version does not meet spec (>=21.0): {line}"
            )

    def test_flake8_package_present(self):
        """Test that flake8 package with correct version is present."""
        req_path = self.get_requirements_path()
        with open(req_path, "r") as f:
            content = f.read()

        assert "flake8" in content, "flake8 package not found in requirements.txt"

        # Find flake8 line
        flake8_lines = [
            line.strip()
            for line in content.split("\n")
            if line.strip().startswith("flake8")
        ]
        assert len(flake8_lines) > 0, "flake8 package malformed"

        # Verify version constraint is >= 3.9.0 or ==
        for line in flake8_lines:
            assert (
                "3.9" in line or "3.10" in line or "4." in line or "5." in line
            ) or ">=3.9" in line, (
                f"flake8 version does not meet spec (>=3.9.0): {line}"
            )

    def test_all_required_packages_present(self):
        """Test that all required packages are present in requirements.txt."""
        req_path = self.get_requirements_path()
        with open(req_path, "r") as f:
            content = f.read()

        required_packages = [
            "requests",
            "pytest",
            "pytest-cov",
            "black",
            "flake8",
        ]

        for package in required_packages:
            assert (
                package in content
            ), f"Required package '{package}' not found in requirements.txt"

    def test_no_local_path_dependencies(self):
        """Test that no local path dependencies are used."""
        req_path = self.get_requirements_path()
        with open(req_path, "r") as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            assert not stripped.startswith("file://"), (
                f"Line {line_num} uses local file:// path: {stripped}"
            )
            assert not stripped.startswith("/"), (
                f"Line {line_num} uses absolute path: {stripped}"
            )
            assert not stripped.startswith("./"), (
                f"Line {line_num} uses relative path: {stripped}"
            )

    def test_no_git_url_dependencies(self):
        """Test that no git URLs are used as dependencies."""
        req_path = self.get_requirements_path()
        with open(req_path, "r") as f:
            content = f.read()

        assert "git+" not in content, (
            "requirements.txt contains git+ URLs which are not allowed"
        )
        assert "git@" not in content, (
            "requirements.txt contains git@ URLs which are not allowed"
        )

    def test_installable_on_pypi(self):
        """Test that requirements are in PyPI-installable format."""
        req_path = self.get_requirements_path()
        with open(req_path, "r") as f:
            lines = f.readlines()

        # Each line should be a valid pip requirement
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # Valid pip requirement format
            # package-name with optional version specifier
            assert re.match(
                r"^[a-zA-Z0-9\-_.]+(\s*[><=!]+.*)?$", stripped
            ), f"Line {line_num} is not a valid pip requirement: {stripped}"
