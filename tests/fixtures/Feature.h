#pragma once
#include "Animal.h"
#include "Flyable.h"

template<typename Self, typename Base>
class StaticObjectInterface : public Base {
};

class Feature : public StaticObjectInterface<Feature, Animal>, public Flyable {
public:
    void speak() const override;
    void fly() const override;
};
