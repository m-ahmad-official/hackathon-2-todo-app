 // Mock global fetch for tests
global.fetch = jest.fn();

// Mock apiClient methods - disabled as tests mock directly
//jest.mock("./api-client", () => ({
//  apiClient: {
//    post: jest.fn(),
//    get: jest.fn(),
//    delete: jest.fn(),
//    put: jest.fn(),
//    patch: jest.fn(),
//  },
//}));

// Mock logging
//jest.mock("./lib/logging", () => ({
//  log_operation: jest.fn(),
//}));

// Mock localStorage for browser environment
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, "localStorage", {
  value: localStorageMock,
});

// Mock window object
global.window = Object.assign({
  location: {
    href: "",
  },
}, global.window || {});

// Mock URLSearchParams
global.URLSearchParams = class URLSearchParams {
  constructor(searchString) {
    this.searchString = searchString;
  }
  toString() {
    return this.searchString;
  }
};