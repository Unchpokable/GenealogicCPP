#pragma once

class Animal {
public:
    virtual ~Animal() = default;
    virtual void speak() const = 0;
};
