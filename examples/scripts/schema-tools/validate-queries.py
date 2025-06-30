#!/usr/bin/env python3
"""
GraphQL Query Validation Script

What it does:
- Validates GraphQL queries against the Healthie schema
- Checks query syntax and field availability
- Provides detailed error reporting
- Helps debug query issues before API calls

Usage:
    python validate-queries.py query.graphql
    python validate-queries.py --query "{ patients { id name } }"
    python validate-queries.py --file queries.json --batch
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Add the MCP server to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from graphql import build_schema, validate, parse, GraphQLError
    from graphql.validation import get_validation_rules
    from healthie_mcp.schema_manager import SchemaManager
    from healthie_mcp.config.settings import get_settings
except ImportError as e:
    print(f"❌ Failed to import required packages: {e}")
    print("Install with: uv add graphql-core")
    sys.exit(1)


class QueryValidator:
    """Validates GraphQL queries against Healthie schema"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.schema = None
        self.schema_content = None
        self._load_schema()
    
    def _load_schema(self):
        """Load GraphQL schema"""
        try:
            settings = get_settings()
            schema_manager = SchemaManager(
                api_endpoint=settings.api_url,
                cache_dir=Path(settings.schema_dir)
            )
            
            self.schema_content = schema_manager.get_schema_content()
            if not self.schema_content:
                print("⚠️  No schema available. Some validations will be limited.")
                return
            
            self.schema = build_schema(self.schema_content)
            print("✅ Schema loaded successfully")
            
        except Exception as e:
            print(f"⚠️  Failed to load schema: {e}")
            print("Query syntax validation will still work.")
    
    def validate_syntax(self, query: str) -> tuple[bool, List[str]]:
        """Validate GraphQL query syntax"""
        try:
            # Parse the query
            document = parse(query)
            return True, []
            
        except GraphQLError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Unexpected error: {e}"]
    
    def validate_against_schema(self, query: str) -> tuple[bool, List[str]]:
        """Validate query against schema"""
        if not self.schema:
            return True, ["Schema not available - skipping schema validation"]
        
        try:
            # Parse the query
            document = parse(query)
            
            # Validate against schema
            validation_errors = validate(self.schema, document)
            
            if validation_errors:
                error_messages = [str(error) for error in validation_errors]
                return False, error_messages
            
            return True, []
            
        except GraphQLError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Unexpected error: {e}"]
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query and provide insights"""
        analysis = {
            'operation_type': None,
            'operation_name': None,
            'fields_requested': [],
            'variables_used': [],
            'complexity_score': 0,
            'depth': 0,
            'recommendations': []
        }
        
        try:
            document = parse(query)
            
            for definition in document.definitions:
                if hasattr(definition, 'operation'):
                    analysis['operation_type'] = definition.operation.value
                    
                    if hasattr(definition, 'name') and definition.name:
                        analysis['operation_name'] = definition.name.value
                    
                    # Analyze selection set
                    if hasattr(definition, 'selection_set'):
                        fields, depth = self._analyze_selection_set(definition.selection_set)
                        analysis['fields_requested'] = fields
                        analysis['depth'] = depth
                        analysis['complexity_score'] = len(fields) * depth
                
                # Extract variables
                if hasattr(definition, 'variable_definitions'):
                    for var_def in definition.variable_definitions:
                        analysis['variables_used'].append(var_def.variable.name.value)
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(analysis)
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_selection_set(self, selection_set, depth: int = 1) -> tuple[List[str], int]:
        """Recursively analyze selection set"""
        fields = []
        max_depth = depth
        
        for selection in selection_set.selections:
            if hasattr(selection, 'name'):
                field_name = selection.name.value
                fields.append(field_name)
                
                # Recursively analyze nested selections
                if hasattr(selection, 'selection_set') and selection.selection_set:
                    nested_fields, nested_depth = self._analyze_selection_set(
                        selection.selection_set, depth + 1
                    )
                    fields.extend([f"{field_name}.{f}" for f in nested_fields])
                    max_depth = max(max_depth, nested_depth)
        
        return fields, max_depth
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on query analysis"""
        recommendations = []
        
        # Complexity recommendations
        if analysis['complexity_score'] > 50:
            recommendations.append(
                "High complexity query - consider breaking into smaller queries"
            )
        
        if analysis['depth'] > 5:
            recommendations.append(
                "Deep nesting detected - may impact performance"
            )
        
        # Field-specific recommendations
        if 'patients' in analysis['fields_requested']:
            recommendations.append(
                "Querying patients - consider using pagination and filters"
            )
        
        if any('appointments' in field for field in analysis['fields_requested']):
            recommendations.append(
                "Querying appointments - consider date range filters"
            )
        
        # Healthcare-specific recommendations
        healthcare_fields = ['medicalHistory', 'clinicalNotes', 'prescriptions']
        if any(field in str(analysis['fields_requested']) for field in healthcare_fields):
            recommendations.append(
                "Accessing clinical data - ensure proper authorization and logging"
            )
        
        return recommendations
    
    def validate_query(self, query: str, name: str = "query") -> Dict[str, Any]:
        """Validate a single query and return detailed results"""
        result = {
            'name': name,
            'query': query,
            'syntax_valid': False,
            'schema_valid': False,
            'syntax_errors': [],
            'schema_errors': [],
            'analysis': {},
            'status': 'unknown'
        }
        
        # Syntax validation
        syntax_valid, syntax_errors = self.validate_syntax(query)
        result['syntax_valid'] = syntax_valid
        result['syntax_errors'] = syntax_errors
        
        if not syntax_valid:
            result['status'] = 'syntax_error'
            return result
        
        # Schema validation
        schema_valid, schema_errors = self.validate_against_schema(query)
        result['schema_valid'] = schema_valid
        result['schema_errors'] = schema_errors
        
        # Query analysis
        result['analysis'] = self.analyze_query(query)
        
        # Determine overall status
        if syntax_valid and schema_valid:
            result['status'] = 'valid'
        elif syntax_valid and not schema_errors:
            result['status'] = 'valid_no_schema'
        else:
            result['status'] = 'invalid'
        
        return result
    
    def validate_batch(self, queries: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Validate multiple queries"""
        results = []
        
        for i, query_info in enumerate(queries):
            if isinstance(query_info, dict):
                name = query_info.get('name', f'query_{i+1}')
                query = query_info.get('query', '')
            else:
                name = f'query_{i+1}'
                query = str(query_info)
            
            result = self.validate_query(query, name)
            results.append(result)
        
        return results
    
    def print_results(self, results: Union[Dict[str, Any], List[Dict[str, Any]]]):
        """Print validation results in a human-readable format"""
        if isinstance(results, dict):
            results = [results]
        
        print("\n" + "=" * 60)
        print("📋 GraphQL Query Validation Results")
        print("=" * 60)
        
        for result in results:
            self._print_single_result(result)
        
        # Summary
        total = len(results)
        valid = sum(1 for r in results if r['status'] == 'valid')
        syntax_errors = sum(1 for r in results if not r['syntax_valid'])
        schema_errors = sum(1 for r in results if not r['schema_valid'])
        
        print("\n" + "=" * 60)
        print("📊 Summary")
        print(f"Total queries: {total}")
        print(f"✅ Valid: {valid}")
        print(f"❌ Syntax errors: {syntax_errors}")
        print(f"⚠️  Schema errors: {schema_errors}")
        
        if valid == total:
            print("🎉 All queries are valid!")
        else:
            print("🔧 Some queries need attention.")
    
    def _print_single_result(self, result: Dict[str, Any]):
        """Print results for a single query"""
        name = result['name']
        status = result['status']
        
        # Status indicator
        if status == 'valid':
            status_icon = "✅"
        elif status == 'valid_no_schema':
            status_icon = "⚠️ "
        else:
            status_icon = "❌"
        
        print(f"\n{status_icon} {name}")
        
        if self.verbose:
            print(f"Query: {result['query'][:100]}{'...' if len(result['query']) > 100 else ''}")
        
        # Syntax errors
        if result['syntax_errors']:
            print("  🚫 Syntax Errors:")
            for error in result['syntax_errors']:
                print(f"    - {error}")
        
        # Schema errors
        if result['schema_errors']:
            print("  ⚠️  Schema Errors:")
            for error in result['schema_errors']:
                print(f"    - {error}")
        
        # Analysis
        analysis = result.get('analysis', {})
        if analysis and self.verbose:
            print("  📊 Analysis:")
            if analysis.get('operation_type'):
                print(f"    Operation: {analysis['operation_type']}")
            if analysis.get('complexity_score'):
                print(f"    Complexity: {analysis['complexity_score']}")
            if analysis.get('depth'):
                print(f"    Depth: {analysis['depth']}")
            
            # Recommendations
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                print("  💡 Recommendations:")
                for rec in recommendations:
                    print(f"    - {rec}")


def load_queries_from_file(file_path: Path) -> List[Dict[str, str]]:
    """Load queries from various file formats"""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    content = file_path.read_text()
    
    if file_path.suffix == '.json':
        # JSON format
        data = json.loads(content)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            raise ValueError("Invalid JSON format")
    
    elif file_path.suffix in ['.graphql', '.gql']:
        # GraphQL file
        return [{'name': file_path.stem, 'query': content}]
    
    else:
        # Assume it's a raw GraphQL query
        return [{'name': file_path.stem, 'query': content}]


def main():
    """Main validation function"""
    parser = argparse.ArgumentParser(description="Validate GraphQL queries against Healthie schema")
    parser.add_argument('file', nargs='?', help="Query file to validate")
    parser.add_argument('--query', '-q', help="Single query string to validate")
    parser.add_argument('--batch', action='store_true', help="Batch validation mode")
    parser.add_argument('--verbose', '-v', action='store_true', help="Verbose output")
    parser.add_argument('--json', action='store_true', help="Output results as JSON")
    parser.add_argument('--output', '-o', help="Output file for results")
    
    args = parser.parse_args()
    
    if not args.file and not args.query:
        parser.error("Must provide either --query or a file path")
    
    validator = QueryValidator(verbose=args.verbose)
    
    try:
        # Determine input source
        if args.query:
            # Single query from command line
            results = validator.validate_query(args.query, "command_line_query")
        else:
            # Load from file
            file_path = Path(args.file)
            queries = load_queries_from_file(file_path)
            
            if args.batch or len(queries) > 1:
                results = validator.validate_batch(queries)
            else:
                results = validator.validate_query(queries[0]['query'], queries[0]['name'])
        
        # Output results
        if args.json:
            output_data = json.dumps(results, indent=2)
            if args.output:
                Path(args.output).write_text(output_data)
                print(f"Results written to {args.output}")
            else:
                print(output_data)
        else:
            validator.print_results(results)
            
            if args.output:
                # Save detailed results
                Path(args.output).write_text(json.dumps(results, indent=2))
                print(f"\nDetailed results saved to {args.output}")
        
        # Exit code based on validation results
        if isinstance(results, list):
            all_valid = all(r['status'] in ['valid', 'valid_no_schema'] for r in results)
        else:
            all_valid = results['status'] in ['valid', 'valid_no_schema']
        
        sys.exit(0 if all_valid else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()