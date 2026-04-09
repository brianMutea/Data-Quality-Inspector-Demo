"""Tests for the CLI module."""

import argparse
import pytest
from unittest.mock import patch, MagicMock
from dqi.cli import main


def test_cli_default_arguments():
    """Test CLI with default arguments."""
    test_args = ['dqi']
    
    with patch('sys.argv', test_args):
        with patch('dqi.cli.fetch_data') as mock_fetch:
            with patch('dqi.cli.check_nulls') as mock_nulls:
                with patch('dqi.cli.check_duplicates') as mock_dups:
                    with patch('dqi.cli.check_outliers') as mock_outliers:
                        with patch('dqi.cli.check_types') as mock_types:
                            with patch('dqi.cli.generate_report') as mock_report:
                                mock_fetch.return_value = (MagicMock(), {})
                                mock_nulls.return_value = {}
                                mock_dups.return_value = {}
                                mock_outliers.return_value = {}
                                mock_types.return_value = {}
                                
                                main()
                                
                                mock_fetch.assert_called_once_with(refresh_cache=False)
                                mock_report.assert_called_once()
                                
                                call_args = mock_report.call_args
                                assert call_args[1]['html_output'] is None
                                assert call_args[1]['assets_dir'] is None


def test_cli_with_html_output():
    """Test CLI with HTML output option."""
    test_args = ['dqi', '--html-output', 'report.html']
    
    with patch('sys.argv', test_args):
        with patch('dqi.cli.fetch_data') as mock_fetch:
            with patch('dqi.cli.check_nulls') as mock_nulls:
                with patch('dqi.cli.check_duplicates') as mock_dups:
                    with patch('dqi.cli.check_outliers') as mock_outliers:
                        with patch('dqi.cli.check_types') as mock_types:
                            with patch('dqi.cli.generate_report') as mock_report:
                                mock_fetch.return_value = (MagicMock(), {})
                                mock_nulls.return_value = {}
                                mock_dups.return_value = {}
                                mock_outliers.return_value = {}
                                mock_types.return_value = {}
                                
                                main()
                                
                                call_args = mock_report.call_args
                                assert call_args[1]['html_output'] == 'report.html'


def test_cli_with_assets_dir():
    """Test CLI with assets directory option."""
    test_args = ['dqi', '--assets-dir', 'reports/assets']
    
    with patch('sys.argv', test_args):
        with patch('dqi.cli.fetch_data') as mock_fetch:
            with patch('dqi.cli.check_nulls') as mock_nulls:
                with patch('dqi.cli.check_duplicates') as mock_dups:
                    with patch('dqi.cli.check_outliers') as mock_outliers:
                        with patch('dqi.cli.check_types') as mock_types:
                            with patch('dqi.cli.generate_report') as mock_report:
                                mock_fetch.return_value = (MagicMock(), {})
                                mock_nulls.return_value = {}
                                mock_dups.return_value = {}
                                mock_outliers.return_value = {}
                                mock_types.return_value = {}
                                
                                main()
                                
                                call_args = mock_report.call_args
                                assert call_args[1]['assets_dir'] == 'reports/assets'


def test_cli_with_all_options():
    """Test CLI with all new options."""
    test_args = [
        'dqi',
        '--output', 'custom_report.md',
        '--html-output', 'custom_report.html',
        '--assets-dir', 'custom_assets',
        '--refresh'
    ]
    
    with patch('sys.argv', test_args):
        with patch('dqi.cli.fetch_data') as mock_fetch:
            with patch('dqi.cli.check_nulls') as mock_nulls:
                with patch('dqi.cli.check_duplicates') as mock_dups:
                    with patch('dqi.cli.check_outliers') as mock_outliers:
                        with patch('dqi.cli.check_types') as mock_types:
                            with patch('dqi.cli.generate_report') as mock_report:
                                mock_fetch.return_value = (MagicMock(), {})
                                mock_nulls.return_value = {}
                                mock_dups.return_value = {}
                                mock_outliers.return_value = {}
                                mock_types.return_value = {}
                                
                                main()
                                
                                mock_fetch.assert_called_once_with(refresh_cache=True)
                                call_args = mock_report.call_args
                                assert call_args[0][5] == 'custom_report.md'
                                assert call_args[1]['html_output'] == 'custom_report.html'
                                assert call_args[1]['assets_dir'] == 'custom_assets'
