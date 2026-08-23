export function formatPrice(price) {
  if (price === null || price === undefined || price === 0) {
    return 'FREE'
  }
  return `R ${price}`
}
