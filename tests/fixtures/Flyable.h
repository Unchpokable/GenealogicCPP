#pragma once

class Flyable {
public:
    virtual ~Flyable() = default;
    virtual void fly() const = 0;
};
