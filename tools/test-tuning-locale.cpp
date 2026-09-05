// Regression for locale-independent tuning parsing and default MIDI frequencies.
// Run: c++ -std=c++20 -O2 -Iinclude/tuning-library tools/test-tuning-locale.cpp -o /tmp/test-tuning-locale
#include "Tunings.h"
#include <cmath>
#include <iostream>
#include <locale>
#include <sstream>
#include <stdexcept>

struct Comma : std::numpunct<char> {
    char do_decimal_point() const override { return ','; }
};

int main()
{
    const auto previous = std::locale::global(std::locale(std::locale::classic(), new Comma));
    for (const auto *value : {"100.0", "-31.174", " 1.25e2", "0.001", "1200.000"}) {
        double expected = 0;
        std::istringstream original(value);
        original.imbue(std::locale("C"));
        original >> expected;
        if (Tunings::locale_atof(value) != expected) throw std::runtime_error("numeric parsing changed");
    }
    const Tunings::Tuning tuning;
    for (int note = 0; note < 128; ++note) {
        const double expected = 440.0 * std::pow(2.0, (note - 69) / 12.0);
        if (std::abs(tuning.frequencyForMidiNote(note) / expected - 1.0) > 1e-12)
            throw std::runtime_error("default tuning changed");
    }
    const auto scale = Tunings::parseSCLData("! test\nDecimal cents\n2\n701.955\n1200.0\n");
    if (std::abs(scale.tones[0].cents - 701.955) > 1e-10)
        throw std::runtime_error("custom Scala tuning changed");
    std::locale::global(previous);
    std::cout << "PASS: decimal parsing, custom scale, and all 128 MIDI frequencies\n";
}
