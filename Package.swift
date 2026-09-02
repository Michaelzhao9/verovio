// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "VerovioToolkit",
    platforms: [
        .iOS(.v16),
        .macOS(.v11)
    ],
    products: [
        .library(
            name: "VerovioToolkit",
            type: .dynamic,
            targets: ["VerovioToolkit"]
        )
    ],
    targets: [
        .target(
            name: "VerovioCore",
            path: ".",
            sources: [
                "src",
                "libmei/dist",
                "libmei/addons",
                "tools/c_wrapper.cpp"
            ],
            publicHeadersPath: "bindings/swift-core",
            cxxSettings: [
                .headerSearchPath("include/crc"),
                .headerSearchPath("include/hum"),
                .headerSearchPath("include/json"),
                .headerSearchPath("include/midi"),
                .headerSearchPath("include/pugi"),
                .headerSearchPath("include/tuning-library"),
                .headerSearchPath("include/utf8"),
                .headerSearchPath("include/vrv"),
                .headerSearchPath("include/zip"),
                .headerSearchPath("libmei/dist"),
                .headerSearchPath("libmei/addons")
            ]
        ),
        .target(
            name: "VerovioToolkit",
            dependencies: ["VerovioCore"],
            path: ".",
            exclude: [
                "CHANGELOG.md", "COPYING", "COPYING.LESSER", "MANIFEST.in", "README.md",
                "Verovio.podspec", "Verovio.xcodeproj", "appveyor.yml", "codemeta.json",
                "pyproject.toml", "setup.py",
                "bindings/go", "bindings/iOS", "bindings/java", "bindings/python", "bindings/swift-core",
                "cmake", "doc", "emscripten", "fonts", "include", "libmei", "src", "tools",
            ],
            sources: ["bindings/swift-toolkit"],
            resources: [.copy("data")]
        )
    ],
    cxxLanguageStandard: .cxx20
)
