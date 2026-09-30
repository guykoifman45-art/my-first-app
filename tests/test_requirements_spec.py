"""Tests for requirements.txt to verify all dependencies are properly specified."""

import re
from pathlib import Path


class TestRequirementsFile:
    """Test suite for requirements.txt file structure and content."""

    REQUIRED_PACKAGES = {
        "requests": ">=2.25.0",
        "pytest": ">=6.0.0",
        "pytest-cov": ">=2.12.0",
        "black": ">=21.0",
        "flake8": ">=3.9.0",
    }

    @property
    def requirements_path(self):
        """Get the path to requirements.txt relative to project root."""
        test_dir = Path(__file__).parent
        project_root = test_dir.parent
        return project_root / "requirements.txt"

    def test_requirements_file_exists(self):
        """Test that requirements.txt file exists in the project root."""
        assert self.requirements_path.exists(), (
            f"requirements.txt not found at {self.requirements_path}"
        )
        assert self.requirements_path.is_file(), (
            f"requirements.txt is not a file at {self.requirements_path}"
        )

    def test_requirements_file_not_empty(self):
        """Test that requirements.txt is not empty."""
        content = self.requirements_path.read_text()
        lines = [line.strip() for line in content.split("\n") if line.strip() and not line.strip().startswith("#")]
        assert len(lines) > 0, "requirements.txt is empty or contains only comments"

    def test_requirements_file_format_valid(self):
        """Test that each requirement line has valid format."""
        content = self.requirements_path.read_text()
        valid_pattern = re.compile(r"^[a-zA-Z0-9\-_.]+\s*(==|>=|<=|<|>|~=)\s*[\d.]+.*$")

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            assert valid_pattern.match(line), (
                f"Invalid requirement format: {line}. "
                "Expected format: 'package-name==version' or 'package-name>=version'"
            )

    def test_required_packages_present(self):
        """Test that all required packages are present in requirements.txt."""
        content = self.requirements_path.read_text()

        for package_name in self.REQUIRED_PACKAGES.keys():
            assert package_name in content, (
                f"Required package '{package_name}' not found in requirements.txt"
            )

    def test_requests_version_correct(self):
        """Test that requests package has correct version constraint."""
        self._verify_package_version("requests", ">=2.25.0")

    def test_pytest_version_correct(self):
        """Test that pytest package has correct version constraint."""
        self._verify_package_version("pytest", ">=6.0.0")

    def test_pytest_cov_version_correct(self):
        """Test that pytest-cov package has correct version constraint."""
        self._verify_package_version("pytest-cov", ">=2.12.0")

    def test_black_version_correct(self):
        """Test that black package has correct version constraint."""
        self._verify_package_version("black", ">=21.0")

    def test_flake8_version_correct(self):
        """Test that flake8 package has correct version constraint."""
        self._verify_package_version("flake8", ">=3.9.0")

    def _verify_package_version(self, package_name, expected_version):
        """Helper method to verify a package has the correct version constraint."""
        content = self.requirements_path.read_text()

        package_line = None
        for line in content.split("\n"):
            line = line.strip()
            if re.match(f"^{re.escape(package_name)}\\s*(==|>=|<=|<|>|~=)", line):
                package_line = line
                break

        assert package_line is not None, (
            f"Package '{package_name}' not found in requirements.txt"
        )

        match = re.search(r"(>=|==|<=|<|>|~=)\s*([\d.]+)", package_line)
        assert match is not None, (
            f"No version constraint found for package '{package_name}' in line: {package_line}"
        )

        operator, version = match.groups()
        # Extract operator and version from expected_version like ">=2.25.0"
        expected_match = re.match(r"(>=|==|<=|<|>|~=)\s*([\d.]+)", expected_version)
        assert expected_match is not None, (
            f"Invalid expected_version format: {expected_version}"
        )
        expected_operator, expected_ver = expected_match.groups()

        assert operator == expected_operator, (
            f"Package '{package_name}' should use '{expected_operator}' operator, "
            f"but found '{operator}' in line: {package_line}"
        )

        assert version == expected_ver, (
            f"Package '{package_name}' version {version} does not match expected {expected_ver}"
        )

    def test_no_local_paths(self):
        """Test that requirements.txt does not contain local file paths."""
        content = self.requirements_path.read_text()

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            assert not line.startswith("file://"), (
                f"Local file path found: {line}"
            )
            assert not line.startswith("/"), (
                f"Absolute path found: {line}"
            )
            assert not line.startswith("."), (
                f"Relative path found: {line}"
            )

    def test_no_git_urls(self):
        """Test that requirements.txt does not contain git URLs."""
        content = self.requirements_path.read_text()

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            assert "git+" not in line.lower(), (
                f"Git URL found: {line}"
            )
            assert "@git" not in line.lower(), (
                f"Git reference found: {line}"
            )

    def test_file_readable_as_text(self):
        """Test that requirements.txt is a valid UTF-8 text file."""
        try:
            content = self.requirements_path.read_text(encoding='utf-8')
            assert isinstance(content, str), (
                "requirements.txt should be readable as text"
            )
            assert len(content) > 0, (
                "requirements.txt should not be empty"
            )
        except UnicodeDecodeError:
            raise AssertionError(
                "requirements.txt is not a valid UTF-8 text file"
            )

    def test_no_duplicate_packages(self):
        """Test that no package is listed more than once."""
        content = self.requirements_path.read_text()
        packages = []

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            package_name = re.split(r"[=<>!~\s]", line)[0].lower()

            assert package_name not in packages, (
                f"Package '{package_name}' is listed more than once"
            )
            packages.append(package_name)

    def test_exactly_required_packages(self):
        """Test that exactly the required packages are present, no more, no less."""
        content = self.requirements_path.read_text()
        found_packages = set()

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            package_name = re.split(r"[=<>!~\s]", line)[0].lower()
            found_packages.add(package_name)

        required_names = set(self.REQUIRED_PACKAGES.keys())
        assert found_packages == required_names, (
            f"Expected packages {required_names}, but found {found_packages}"
        )

    def test_no_editable_installs(self):
        """Test that requirements.txt does not contain editable installs (-e flag)."""
        content = self.requirements_path.read_text()

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            assert not line.startswith("-e "), (
                f"Editable install (-e) found: {line}"
            )

    def test_no_environment_markers(self):
        """Test that requirements.txt does not contain environment markers."""
        content = self.requirements_path.read_text()

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Environment markers use semicolon, which we expect not to find
            # since we want simple, universal requirements
            if ";" in line:
                raise AssertionError(
                    f"Environment marker found: {line}. "
                    "Requirements should be universal without platform-specific markers."
                )
