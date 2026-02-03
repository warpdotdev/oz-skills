# Screen Reader Testing Guide

Manual testing with screen readers is essential for accessibility validation. Automated tools only catch 30-57% of issues.

## Testing Checklist

### Keyboard Navigation
- [ ] Tab through entire page, use Enter/Space to activate
- [ ] Can reach all interactive elements
- [ ] Focus order is logical and follows visual order
- [ ] No keyboard traps
- [ ] Skip links work properly

### Screen Reader Testing
- [ ] Test with VoiceOver (Mac), NVDA (Windows), or TalkBack (Android)
- [ ] All images have meaningful alt text or are properly marked decorative
- [ ] Form labels are announced correctly
- [ ] Heading structure makes sense
- [ ] Links are descriptive
- [ ] Error messages are announced
- [ ] Dynamic content updates are announced (live regions)

### Visual Testing
- [ ] Content usable at 200% zoom
- [ ] Content reflows without horizontal scroll at 320px width
- [ ] Color contrast meets WCAG requirements
- [ ] Content visible in Windows High Contrast Mode

### Motion & Animation
- [ ] Test with `prefers-reduced-motion: reduce`
- [ ] Animations can be paused/stopped
- [ ] No content flashes more than 3 times per second

## Screen Reader Commands

### VoiceOver (macOS)

| Action | Command |
|--------|---------|
| Start/Stop | ⌘ + F5 |
| Navigate next | VO + → |
| Navigate previous | VO + ← |
| Activate element | VO + Space |
| Read from current position | VO + A |
| Stop reading | Control |
| Open rotor | VO + U |
| Navigate by headings | VO + ⌘ + H |
| Navigate by links | VO + ⌘ + L |
| Navigate by form controls | VO + ⌘ + J |
| Navigate by landmarks | VO + ⌘ + W |

**Note:** VO = Control + Option

### NVDA (Windows)

| Action | Command |
|--------|---------|
| Start/Stop | Ctrl + Alt + N |
| Navigate next | ↓ |
| Navigate previous | ↑ |
| Activate element | Enter |
| Read from current position | NVDA + ↓ |
| Stop reading | Ctrl |
| Elements list | NVDA + F7 |
| Next heading | H |
| Previous heading | Shift + H |
| Next link | K |
| Previous link | Shift + K |
| Next form field | F |
| Previous form field | Shift + F |
| Next landmark | D |
| Previous landmark | Shift + D |

**Note:** NVDA = Insert (or Caps Lock if configured)

### JAWS (Windows)

| Action | Command |
|--------|---------|
| Navigate next | ↓ |
| Navigate previous | ↑ |
| Next heading | H |
| Previous heading | Shift + H |
| Next link | Tab or K |
| Next form field | F |
| Next landmark | R |
| Elements list | Insert + F3 |
| Forms list | Insert + F5 |
| Links list | Insert + F7 |
| Headings list | Insert + F6 |

### TalkBack (Android)

| Action | Gesture |
|--------|---------|
| Activate | Double-tap |
| Navigate next | Swipe right |
| Navigate previous | Swipe left |
| Scroll down | Two-finger swipe up |
| Scroll up | Two-finger swipe down |
| Global context menu | Swipe down then right |
| Local context menu | Swipe up then right |
| Reading controls | Swipe left then right |

## Common Testing Scenarios

### Test Form Submission
1. Navigate to form with screen reader
2. Verify each label is announced
3. Fill out form using keyboard only
4. Submit with invalid data
5. Verify error messages are announced
6. Verify focus moves to first error
7. Fix errors and submit successfully

### Test Modal/Dialog
1. Open modal with keyboard
2. Verify focus moves to modal
3. Verify modal title is announced
4. Tab through modal elements
5. Verify focus stays trapped in modal
6. Press Escape to close
7. Verify focus returns to trigger element

### Test Dynamic Content
1. Trigger content update
2. Verify screen reader announces change
3. Check if announcement is polite or assertive
4. Verify new content is focusable if needed

### Test Navigation
1. Navigate to page with screen reader
2. Use rotor/elements list to view headings
3. Verify heading hierarchy makes sense
4. Use landmarks to navigate page sections
5. Verify skip link appears on focus
6. Test skip link functionality

## Setting Up Screen Readers

### VoiceOver (macOS)
- Built into macOS
- Enable: System Preferences → Accessibility → VoiceOver
- Quick toggle: ⌘ + F5
- VoiceOver Utility for settings: `/System/Library/CoreServices/VoiceOver.app`
- Practice mode: VoiceOver Utility → Quick Start

### NVDA (Windows)
- Free, open source
- Download: https://www.nvaccess.org/
- Portable version available
- Add-ons available for enhanced testing
- Can run alongside JAWS

### JAWS (Windows)
- Commercial (expensive)
- Download: https://www.freedomscientific.com/
- 40-minute demo mode available
- Most commonly used by professionals
- Excellent for professional testing

### TalkBack (Android)
- Built into Android
- Enable: Settings → Accessibility → TalkBack
- Tutorial available on first run
- Test on real device preferred over emulator

## Browser Extensions for Testing

### axe DevTools
- Available for Chrome, Firefox, Edge
- Free browser extension
- Automated testing + guided tests
- https://www.deque.com/axe/

### WAVE
- Browser extension
- Visual feedback on accessibility issues
- https://wave.webaim.org/extension/

### Lighthouse
- Built into Chrome DevTools
- Accessibility audit included
- DevTools → Lighthouse tab

## Best Practices

### Do
- Test with actual screen reader users when possible
- Test on multiple screen readers
- Test with keyboard only before using screen reader
- Document issues with screenshots and recordings
- Test in different browsers
- Test on mobile devices

### Don't
- Rely solely on automated testing
- Assume one screen reader represents all
- Test only in one browser
- Skip keyboard-only testing
- Ignore warnings from automated tools
- Test only desktop (mobile is critical)

## Common Issues to Listen For

- Form fields with no label
- Images with no alt text or poor alt text
- Links with non-descriptive text ("click here")
- Headings out of order or missing
- Tables with no headers
- Live regions not announcing updates
- Modal dialogs not announced
- Focus moving unexpectedly
- Content only available visually (color, position)
- Redundant or verbose announcements

## Resources

- [WebAIM Screen Reader Testing](https://webaim.org/articles/screenreader_testing/)
- [Deque University](https://dequeuniversity.com/)
- [A11Y Project Screen Reader Guides](https://www.a11yproject.com/posts/getting-started-with-screen-readers/)
- [VoiceOver User Guide](https://support.apple.com/guide/voiceover/welcome/mac)
- [NVDA User Guide](https://www.nvaccess.org/files/nvda/documentation/userGuide.html)
