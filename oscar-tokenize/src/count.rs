use std::{cmp::Ordering, fmt::Display};

use derive_more::{Add, AddAssign, Constructor, Sum};

#[derive(
    Copy, Clone, Debug, Add, AddAssign, Constructor, Sum, PartialEq, Eq, PartialOrd, Ord, Default,
)]
pub struct Count(u64);

impl Count {
    #[allow(dead_code)]
    #[must_use]
    pub fn by_desc(&self, other: &Count) -> Ordering {
        self.0.cmp(&other.0).reverse()
    }
    #[must_use]
    pub fn by_key_desc(self) -> impl Ord {
        u64::MAX - self.0
    }
    #[must_use]
    pub fn into_inner(self) -> u64 {
        self.0
    }
    #[must_use]
    pub fn float(self) -> f64 {
        self.0 as f64
    }
}

impl Display for Count {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        const UNITS: [&str; 6] = ["", "K", "M", "B", "T", "Q"];

        let &Count(value) = self;
        let value = value as f64;

        let units_values = (0..UNITS.len())
            .map(u32::try_from)
            .map(Result::unwrap)
            .zip(UNITS)
            .map(|(index, unit)| (u64::pow(10, index * 3) as f64, unit))
            .rev();

        for (base_entry, unit) in units_values {
            if value < base_entry {
                continue;
            }
            #[allow(
                clippy::cast_sign_loss,
                reason = "Logarithm of value >1 is non-negative"
            )]
            let digits = if unit.is_empty() {
                0
            } else {
                2 - (value / base_entry).log10().floor() as usize
            };
            let number_string = format!("{:.*}", digits, value / base_entry);
            write!(f, "{number_string:>5}{unit}")?;
            break;
        }

        Ok(())
    }
}

impl Add<u64> for Count {
    type Output = Self;

    fn add(self, other: u64) -> Self::Output {
        Self(self.0 + other)
    }
}

impl AddAssign<u64> for Count {
    fn add_assign(&mut self, other: u64) {
        self.0 += other;
    }
}
