"""
Command-line interface for the AI Geometry Tutor.
"""

import sys
import argparse
from .tutor import GeometryTutor
from .llm_utils import setup_environment


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Geometry Tutor for Vietnamese High School Students"
    )
    parser.add_argument(
        "--problem", type=str, help="Geometry problem text (in Vietnamese)"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Start interactive mode"
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    args = parser.parse_args()

    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed. Please check your API key configuration.")
        sys.exit(1)

    # Create tutor instance
    tutor = GeometryTutor()

    if args.problem:
        # Direct problem mode
        print(f"🔍 Giải quyết bài toán: {args.problem}")
        result = tutor.start_new_problem(args.problem)

        if not result["success"]:
            print(f"❌ Lỗi: {result['error']}")
            sys.exit(1)

        print(f"✅ {result['message']}")

    elif args.interactive:
        # Interactive mode
        interactive_mode(tutor)

    else:
        # Default: show help and prompt for problem
        print("🚀 AI Geometry Tutor")
        print("=" * 50)
        print("Nhập bài toán hình học (tiếng Việt):")
        problem = input("👤 Bài toán: ").strip()

        if problem:
            result = tutor.start_new_problem(problem)
            if not result["success"]:
                print(f"❌ Lỗi: {result['error']}")
                sys.exit(1)
        else:
            print("❌ Vui lòng nhập bài toán!")
            sys.exit(1)


def interactive_mode(tutor: GeometryTutor):
    """Interactive CLI mode."""
    print("🎓 Chế độ tương tác AI Geometry Tutor")
    print("=" * 50)
    print("Nhập 'quit' để thoát")

    while True:
        try:
            line = input("👤 Nhập bài toán hình học: ").strip()
            problem = line
            while line:
                line = input()
                problem += "\n" + line.strip()

            problem = problem.strip()

            if not problem:
                print("❌ Vui lòng nhập bài toán!")
                continue

            if problem.lower() in ["quit", "exit", "q"]:
                print("👋 Tạm biệt!")
                break

            result = tutor.start_new_problem(problem)

            if not result["success"]:
                print(f"❌ Lỗi: {result['error']}")
                continue

            print(f"✅ {result['message']}")

        except KeyboardInterrupt:
            print("👋 Tạm biệt!")
            break
        except Exception as e:
            print(f"❌ Lỗi không mong muốn: {e}")


if __name__ == "__main__":
    main()
