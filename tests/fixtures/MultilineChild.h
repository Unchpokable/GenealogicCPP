#pragma once
#include "Dog.h"
#include "Flyable.h"

class MultilineChild
    : public Dog
    , public Flyable {
public:
    void speak() const override;
    void fly() const override;
};
