import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
          <div className="text-center">
            <p className="text-6xl mb-4">😵</p>
            <h1 className="text-2xl font-bold text-gray-700 mb-2">문제가 생겼어요</h1>
            <p className="text-sm text-gray-400 mb-8">잠시 후 다시 시도해주세요</p>
            <button
              onClick={() => window.location.replace("/diary")}
              className="bg-indigo-500 hover:bg-indigo-600 text-white px-6 py-2 rounded-full text-sm font-medium transition"
            >
              처음으로 가기
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
